"""
Build and query text features of each document.
AI method shoud go through IServerConn interface.
"""
import os, sys, hashlib
import asyncio
import requests
from typing import TypedDict, TYPE_CHECKING, Optional, Callable, Literal
from resbibman.confReader import DOC_SUMMARY_DIR, VECTOR_DB_PATH
from resbibman.core.dataClass import DataBase, DataPoint
from resbibman.core.pdfTools import getPDFText
from resbibman.core.serverConn import IServerConn
from resbibman.core.asynciolib import asyncioLoopRun
from resbibman.core.utils import Timer
from resbibman.core import globalVar as G
import tiny_vectordb

if sys.version_info < (3, 9):
    from typing import Iterator
else:
    from collections.abc import Iterator

if TYPE_CHECKING:
    from iRBM.lmInterface import StreamIterType

def createSummaryWithLLM(iconn: IServerConn, text: str, verbose: bool = False) -> str:
    summary = ""
    res = iconn.chat(
        conv_dict={
            "system": "A conversation between a human and an AI research assistant. "\
                "The AI gives short and conscise response in academic literature style. ",
            "conversations": []
        },
        prompt = "Summarize the following paper in about 100 words, "\
            "your summary should focus on the motivation and contribution. "\
            "Don't mention title."
            f"Here is the paper: {text}",
        model_name = "gpt-3.5-turbo"
    )
    if not res:
        return ""
    try:
        for t in res:
            summary += t
        if verbose:
            print(summary)
    except requests.exceptions.ChunkedEncodingError:
        # may be caused by too long response
        return ""
    return summary

FeatureQueryResult = TypedDict("FeatureQueryResult", {"uids": list[str], "scores": list[float]})

def getFeatureTextSource(
        iconn: IServerConn, 
        dp: DataPoint, 
        max_words_per_doc: Optional[int] = None, 
        print_fn: Callable[[str], None] = lambda x: None
        ) -> tuple[str, Literal["abstract", "summary", "fulltext", "title"]]:
    """
    Extract text source from a document for feature extraction.
    return text_source, source_type
    """
    abstract = dp.fm.readAbstract()
    uid = dp.uuid
    title_text: str = "Title: " + dp.title + "\n"
    if abstract:
        # if abstract is available, use it as the text source
        print_fn(f"- use abstract")
        return title_text + abstract, "abstract"
    elif dp.fm.hasFile() and dp.fm.file_extension == ".pdf":
        # if has pdf, try to create a summary
        pdf_path = dp.fm.file_p; assert pdf_path
        pdf_text = getPDFText(pdf_path, max_words_per_doc)

        _summary_cache_path = os.path.join(DOC_SUMMARY_DIR, uid + ".txt")
        if os.path.exists(_summary_cache_path):
            # check if summary is already created
            summary = open(_summary_cache_path, "r").read()
            print_fn(f"- use cached summary")
        else:
            summary = createSummaryWithLLM(iconn, pdf_text)
            with open(_summary_cache_path, "w") as f:
                f.write(summary)
            if summary:
                print_fn(f"- use LLM summary")

        if summary:
            # if summary is created, use it as the text source
            return title_text + summary, "summary"
        else:
            # otherwise, use the full text
            print_fn(f"- use full text")
            return pdf_text, "fulltext"
    else:
        # otherwise, use title
        print_fn(f"- use title")
        return title_text.strip(), "title"

def buildFeatureStorage(
        db: DataBase, 
        max_words_per_doc: int = 2048, 
        force = False
        ):
    vector_db = tiny_vectordb.VectorDatabase(VECTOR_DB_PATH, [{"name": "doc_feature", "dimension": 768}])
    vector_collection = vector_db.getCollection("doc_feature")

    # a file to store the source text hash, to avoid repeated featurization
    doc_feature_src_hash_log = os.path.join(os.path.dirname(VECTOR_DB_PATH), "doc_feature_src_hash.log")
    doc_feature_src_hash = {}       # uid -> hash of the source text
    if not os.path.exists(doc_feature_src_hash_log):
        with open(doc_feature_src_hash_log, "w") as f:
            f.write(r"")

    if force:
        vector_collection.deleteBlock(vector_collection.keys())
    else:
        # load existing features source record
        with open(doc_feature_src_hash_log, "r") as f:
            lines = f.readlines()
            for line in lines:
                if not line.strip():
                    continue
                uid, hash = line.strip().split(":")
                doc_feature_src_hash[uid] = hash
    
    iconn = IServerConn()
    text_src: dict[str, str] = {}       # uid -> text source for featurization
    
    # extract text source
    for idx, (uid, dp) in enumerate(db.items()):
        # if idx > 100:
        #     # for debug
        #     break
        text_src[uid], src_type = getFeatureTextSource(iconn, dp, max_words_per_doc)
        print(f"[Extracting source] ({idx}/{len(db)}) <{src_type}>: {uid}...")

    # featurize the summary
    async def _featurize(text) -> list[float] | None:
        res = iconn.featurize(text)
        return res 
    
    # build update dict
    print(f"Checking {len(text_src)} documents signature...")
    text_src_update = {}
    _current_feature_keys = vector_collection.keys()
    for uid, text in text_src.items():
        if uid not in _current_feature_keys:
            text_src_update[uid] = text
        else:
            # check if the feature is outdated
            hash = hashlib.sha256(text.encode()).hexdigest()
            if hash != doc_feature_src_hash[uid]:
                text_src_update[uid] = text

    print(f"Featurizing {len(text_src_update)} documents...")
    uid_list = list(text_src_update.keys())
    text_list = list(text_src_update.values())
    tasks = [ _featurize(text) for text in text_list ]
    feature_list: list[list[float] | None] = asyncioLoopRun(asyncio.gather(*tasks))

    _to_record_uids = []
    _to_record_features = []
    for uid, feature_item in zip(uid_list, feature_list):
        # traverse the result and record the feature source hash
        # also filter out failed featurization
        if feature_item is None:
            print(f"Warning: failed to featurize {uid}")
            continue
        doc_feature_src_hash[uid] = hashlib.sha256(text_src[uid].encode()).hexdigest()
        _to_record_uids.append(uid)
        _to_record_features.append(feature_item)
    vector_collection.setBlock(_to_record_uids, _to_record_features)
    vector_db.flush()
    vector_db.commit()
    with open(doc_feature_src_hash_log, "w") as f:
        for uid, hash in doc_feature_src_hash.items():
            f.write(f"{uid}:{hash}\n")
    
    print(f"Saved feature index to {VECTOR_DB_PATH}")

def queryFeatureIndex(
        query: str, n_return: int = 16, 
        vector_collection: Optional[tiny_vectordb.VectorCollection] = None) -> FeatureQueryResult:
    if not vector_collection:
        with Timer("Loading vector db"):
            vector_collection = tiny_vectordb.VectorDatabase(VECTOR_DB_PATH, [{"name": "doc_feature", "dimension": 768}])["doc_feature"]
    iconn = IServerConn()
    query_vec = iconn.featurize(query) # [d_feature]
    assert query_vec is not None

    uids, scores = vector_collection.search(query_vec, n_return)
    return {
        "uids": uids,
        "scores": scores
    }

def queryFeatureIndexByUID(db: DataBase, query_uid: str, n_return: int = 16) -> FeatureQueryResult:
    """
    query the related documents of the given uid
    """
    # read the document with the given uid
    pdf_path = db[query_uid].file_path
    if pdf_path is None:
        query_string: str = db[query_uid].title
        print("Warning: no pdf file found, use title only: {}".format(query_string))
    else:
        query_string = getPDFText(pdf_path, 4096)
    return queryFeatureIndex(query_string, n_return)

