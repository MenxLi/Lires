"""
Build and query text features of each document.
AI method shoud go through IServerConn interface.
"""
from __future__ import annotations
import os, hashlib, re
import asyncio
from typing import TypedDict, Optional, Callable, Literal, TYPE_CHECKING
from lires.config import DOC_SUMMARY_DIR, VECTOR_DB_PATH
from lires.core.dataClass import DataBase, DataPoint
from lires.core.pdfTools import getPDFText
from lires.utils import Timer
import tiny_vectordb
if TYPE_CHECKING:
    from lires.api import IServerConn

async def createSummaryWithLLM(iconn: IServerConn, text: str, verbose: bool = False) -> str:
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
        model_name = "DEFAULT"
    )
    async for t in res:
        summary += t
        if verbose:
            print(summary)
    return summary

FeatureQueryResult = TypedDict("FeatureQueryResult", {"uids": list[str], "scores": list[float]})

FeatureTextSourceT = TypedDict("FeatureTextSource", {
            "text": str, 
            "hash": str,
            "type": Literal["abstract", "summary", "fulltext", "title"]},
            )
async def getFeatureTextSource(
        iconn: Optional[IServerConn], 
        dp: DataPoint, 
        max_words_per_doc: Optional[int] = None, 
        print_fn: Callable[[str], None] = lambda x: None
        )-> FeatureTextSourceT:
    """
    Extract text source from a document for feature extraction.
    Priority: abstract > ai summary > fulltext > title
    - iconn: IServerConn, if set to None, will not use LLM to create summary
    - dp: DataPoint
    - max_words_per_doc: int, if set to None, will not truncate the text
    - print_fn: Callable[[str], None], a function to print the progress
    """
    abstract = await dp.fm.readAbstract()
    uid = dp.uuid
    title_text: str = "Title: " + dp.title + "\n"
    if abstract:
        # if abstract is available, use it as the text source
        print_fn(f"- use abstract")
        return {
            "text": (_text := title_text + abstract),
            "hash": hashlib.sha256(_text.encode()).hexdigest(),
            "type": "abstract"
        }
    elif await dp.fm.hasFile() and dp.summary.file_type == ".pdf":
        # if has pdf, try to create a summary
        pdf_path = await dp.fm.filePath(); assert pdf_path
        pdf_text = await getPDFText(pdf_path, max_words_per_doc)

        _summary_cache_path = os.path.join(DOC_SUMMARY_DIR, uid + ".txt")
        if os.path.exists(_summary_cache_path):
            # check if summary is already created
            summary = open(_summary_cache_path, "r").read()
            print_fn(f"- use cached summary")
        else:
            if iconn:
                # if LLM is available, use it to create summary
                summary = await createSummaryWithLLM(iconn, pdf_text)
                with open(_summary_cache_path, "w") as f:
                    f.write(summary)
                if summary:
                    print_fn(f"- use LLM summary")
            else:
                summary = ""

        if summary:
            # if summary is created, use it as the text source
            return {
                "text": (_text := title_text + summary),
                "hash": hashlib.sha256(_text.encode()).hexdigest(),
                "type": "summary"
            }
        else:
            # otherwise, use the full text
            print_fn(f"- use full text")
            return {
                "text": (_text := pdf_text),
                "hash": hashlib.sha256(_text.encode()).hexdigest(),
                "type": "fulltext"
            }
    else:
        # otherwise, use title
        print_fn(f"- use title")
        return {
            "text": (_text := title_text.strip()),
            "hash": hashlib.sha256(_text.encode()).hexdigest(),
            "type": "title"
        }

async def buildFeatureStorage(
        iconn: IServerConn,
        db: DataBase, 
        vector_db: tiny_vectordb.VectorDatabase,
        max_words_per_doc: int = 2048, 
        use_llm: bool = True,
        force = False,
        operation_interval: float = 0.,
        ):
    """
    - operation_interval: float, the interval between two operations, in seconds, 
        set this to a positive value to avoid blocking the main event loop
    """
    # vector_db = tiny_vectordb.VectorDatabase(VECTOR_DB_PATH, [{"name": "doc_feature", "dimension": 768}])
    vector_collection = vector_db.getCollection("doc_feature")

    # check if ai server is running
    assert iconn.status is not None, "iServer is not running, please connect to the AI server fist"

    # a file to store the source text hash, to avoid repeated featurization
    __vec_db_path = vector_db.database_path
    text_src_hash_log = os.path.join(os.path.dirname(__vec_db_path), "doc_feature_src_hash.log")

    text_src_hash = {}               # uid -> hash of the source text
    text_src_hash_record = {}        # uid -> hash of the source text
    if not os.path.exists(text_src_hash_log):
        with open(text_src_hash_log, "w") as f:
            f.write(r"")

    if force:
        vector_collection.deleteBlock(vector_collection.keys())
        os.remove(text_src_hash_log)
    else:
        # load existing features source record
        with open(text_src_hash_log, "r") as f:
            lines = f.readlines()
            for line in lines:
                if not line.strip():
                    continue
                hash = (__split := line.strip().split(":"))[-1]
                uid = ":".join(__split[:-1])
                text_src_hash_record[uid] = hash
    
    text_src: dict[str, str] = {}       # uid -> text source for featurization
    
    # extract text source
    for idx, dp in enumerate(await db.getAll()):
        uid = dp.uuid
        # if idx > 3: break # for debug
        await asyncio.sleep(operation_interval)
        _ret = await getFeatureTextSource(iconn if use_llm else None, dp, max_words_per_doc)
        text_src[uid] = _ret["text"]
        src_type = _ret["type"]
        text_src_hash[uid] = _ret["hash"]

        print(f"[Extracting source] ({idx}/{await db.count()}) <{src_type}>: {uid}...")

    # build update dict
    print(f"Checking {len(text_src)} documents signature...")
    text_src_update = {}
    _current_feature_keys = vector_collection.keys()
    for uid, text in text_src.items():
        if uid not in _current_feature_keys:
            text_src_update[uid] = text
        else:
            # check if the feature is outdated
            if text_src_hash[uid] != text_src_hash_record[uid]:
                text_src_update[uid] = text

    print(f"Featurizing {len(text_src_update)} documents...")
    uid_list = list(text_src_update.keys())
    text_list = list(text_src_update.values())

    feature_list = []
    for text in text_list:
        await asyncio.sleep(operation_interval)
        feature_list.append(await iconn.featurize(text))

    _to_record_uids = []
    _to_record_features = []
    for uid, feature_item in zip(uid_list, feature_list):
        # traverse the result and record the feature source hash
        # also filter out failed featurization
        # if feature_item is None:
        #     print(f"Warning: failed to featurize {uid}")
        #     continue
        text_src_hash_record[uid] = text_src_hash[uid] 
        _to_record_uids.append(uid)
        _to_record_features.append(feature_item)
    vector_collection.setBlock(_to_record_uids, _to_record_features)
    vector_db.commit()
    with open(text_src_hash_log, "w") as f:
        for uid, hash in text_src_hash_record.items():
            f.write(f"{uid}:{hash}\n")
    
    print(f"Saved feature index to {__vec_db_path}, source log to {text_src_hash_log}")

async def queryFeatureIndex(
        iconn: IServerConn,
        vector_collection: tiny_vectordb.VectorCollection,
        query: str, n_return: int = 16, 
        ) -> FeatureQueryResult:
    if not vector_collection:
        with Timer("Loading vector db"):
            vector_collection = tiny_vectordb.VectorDatabase(VECTOR_DB_PATH, [{"name": "doc_feature", "dimension": 768}])["doc_feature"]
    query_vec = await iconn.featurize(query) # [d_feature]
    assert query_vec is not None

    uids, scores = vector_collection.search(query_vec, n_return)
    return {
        "uids": uids,
        "scores": scores
    }

async def queryFeatureIndexByUID(
    db: DataBase, 
    iconn: IServerConn,
    vector_collection: tiny_vectordb.VectorCollection,
    query_uid: str, 
    n_return: int = 16
    ) -> FeatureQueryResult:
    """
    query the related documents of the given uid
    """
    # read the document with the given uid
    pdf_path = await (dp:=await db.get(query_uid)).fm.filePath()
    if pdf_path is None:
        query_string: str = dp.title
        print("Warning: no pdf file found, use title only: {}".format(query_string))
    else:
        query_string = await getPDFText(pdf_path, 4096)
    return await queryFeatureIndex(
        iconn=iconn,
        vector_collection=vector_collection,
        query=query_string, 
        n_return=n_return
        )


async def retrieveRelevantSections(
        iconn: IServerConn,
        query_text: str, 
        src_text: str, 
        n_max_return = 5,
        min_split_words: int = 128,
        min_score = 0.2,
        verbose = False
        ) -> list[tuple[str, float]]:
    assert iconn.status is not None, "iServer is not running, please connect to the AI server fist"

    if verbose: print("Querying relevent sections...")

    sentences = src_text.replace("\n", " ").split(". ")

    for i in range(len(sentences)):
        sentences[i] = sentences[i].strip()

        # merge the sentences if the length is too short
        if len(sentences[i].split(" ")) < min_split_words:
            if i == len(sentences) - 1:
                break
            sentences[i+1] = sentences[i] + ". " + sentences[i+1]
            sentences[i] = ""

    if verbose: print(f"Found {len(sentences)} sentences")
    sentences = [s for s in sentences if s != ""]

    # featurize the sentences
    # split the text into sections
    if verbose: print(f"Query: {query_text}")
    query_text = query_text.replace("\n", " ")
    query_vec = await iconn.featurize(query_text)

    __non_english_regex = re.compile(r'[^a-zA-Z0-9\s\.\,\;\:\!\?\-\'\"\(\)\[\]\{\}\&\%\$\#\@\!\~\`\+\=\_\\\/\*\^]+')
    def __containsNoneEnglish(sentence):
        return bool(__non_english_regex.findall(sentence))

    src_vec_dict: dict[str, list[float]] = {}
    for sentence in sentences:
        await asyncio.sleep(0)
        # TODO: replace this
        # ignore sentences with none english words
        if __containsNoneEnglish(sentence):
            continue

        sentence_feat = await iconn.featurize(sentence)
        src_vec_dict[sentence] = sentence_feat
    
    # compute the similarity
    vec_col = tiny_vectordb.VectorCollection(None, "_feature", 768)
    vec_col.addBlock(
        list(src_vec_dict.keys()), 
        list(src_vec_dict.values())
        )     # requires python > 3.7
    search_res = vec_col.search(query_vec, n_max_return)

    ret = [(sentence, score) for sentence, score in zip(search_res[0], search_res[1]) if score > min_score]
    ret.sort(key=lambda x: x[1], reverse=True) # sort by score, descending
    return ret

