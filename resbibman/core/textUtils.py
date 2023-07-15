"""
Build and query text features of each document.
AI method shoud go through IServerConn interface.
"""
import os, sys, hashlib
import asyncio
from asyncio import Future
import tqdm, requests
from typing import TypedDict, TYPE_CHECKING, Callable, Any
import torch
from resbibman.confReader import DOC_FEATURE_PATH, DOC_SUMMARY_DIR
from resbibman.core.dataClass import DataBase, DataPoint
from resbibman.core.pdfTools import getPDFText
from resbibman.core.serverConn import IServerConn
from resbibman.core.asynciolib import asyncioLoopRun

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


class FeatureItem(TypedDict):
    feature: torch.Tensor
    hash: str       # indicate the source of the feature
FeatureDict = dict[str, FeatureItem]
FeatureQueryResult = TypedDict("FeatureQueryResult", {"uids": list[str], "scores": list[float]})
def buildFeatureStorage(
        db: DataBase, 
        max_words_per_doc: int = 2048, 
        force = False
        ):
    if os.path.exists(DOC_FEATURE_PATH) and not force:
        feature_dict = torch.load(DOC_FEATURE_PATH)
    else:
        feature_dict = {}
    
    iconn = IServerConn()
    text_src: dict[str, str] = {}       # uid -> text source for featurization
    
    
    for idx, (uid, dp) in enumerate(db.items()):
        # if idx > 20:
        #     # for debug
        #     break
        print(f"[Extracting source] ({idx}/{len(db)}) {uid}...")
        abstract = dp.fm.readAbstract()
        title_text: str = "Title: " + dp.title + "\n"
        if abstract:
            # if abstract is available, use it as the text source
            text_src[uid] = title_text + abstract
            print(f"- use abstract")
        elif dp.fm.hasFile() and dp.fm.file_extension == ".pdf":
            # if has pdf, try to create a summary
            pdf_path = dp.fm.file_p; assert pdf_path
            pdf_text = getPDFText(pdf_path, max_words_per_doc)

            _summary_cache_path = os.path.join(DOC_SUMMARY_DIR, uid + ".txt")
            if os.path.exists(_summary_cache_path):
                # check if summary is already created
                summary = open(_summary_cache_path, "r").read()
                print(f"- use cached summary")
            else:
                summary = createSummaryWithLLM(iconn, pdf_text)
                with open(_summary_cache_path, "w") as f:
                    f.write(summary)
                if summary:
                    print(f"- use LLM summary")

            if summary:
                # if summary is created, use it as the text source
                text_src[uid] = title_text + summary
            else:
                # otherwise, use the full text
                text_src[uid] = pdf_text
                print(f"- use full text")
        else:
            # otherwise, use title
            text_src[uid] = title_text.strip()
            print(f"- use title")

    # featurize the summary
    async def _featurize(text) -> list | None:
        res = iconn.featurize(text)
        return res 
    
    # build update dict
    print(f"Checking {len(text_src)} documents signature...")
    text_src_update = {}
    for uid, text in text_src.items():
        if uid not in feature_dict:
            text_src_update[uid] = text
        else:
            # check if the feature is outdated
            feature_item = feature_dict[uid]
            hash = hashlib.sha256(text.encode()).hexdigest()
            if hash != feature_item["hash"]:
                text_src_update[uid] = text

    print(f"Featurizing {len(text_src_update)} documents...")
    uid_list = list(text_src_update.keys())
    text_list = list(text_src_update.values())
    tasks = [ _featurize(text) for text in text_list ]
    feature_list = asyncioLoopRun(asyncio.gather(*tasks))

    for uid, feature_item in zip(uid_list, feature_list):
        if feature_item is None:
            print(f"Warning: failed to featurize {uid}")
            continue
        feature_dict[uid] = {
            "feature": torch.tensor(feature_item),
            "hash": hashlib.sha256(text_src[uid].encode()).hexdigest()
        }
    
    torch.save(feature_dict, DOC_FEATURE_PATH)
    print(f"Saved feature index to {DOC_FEATURE_PATH}")

g_feature_dict: FeatureDict | None = None
def queryFeatureIndex(query: str, n_return: int = 16) -> FeatureQueryResult:
    global g_feature_dict
    iconn = IServerConn()
    if g_feature_dict is None:
        if os.path.exists(DOC_FEATURE_PATH):
            g_feature_dict = torch.load(DOC_FEATURE_PATH)
        else:
            raise FileNotFoundError("Feature index not found, please build the index storage first")

    assert g_feature_dict
    feature_dict: FeatureDict = g_feature_dict

    query_vec = iconn.featurize(query) # [d_feature]
    assert query_vec is not None
    query_vec = torch.tensor(query_vec)

    if len(feature_dict) == 0:
        raise ValueError("Feature index is empty, please build the index storage first")

    # collect uuid and features in to a large chunk for batch processing
    uuids = []
    features = []
    for uid, feature_item in feature_dict.items():
        uuids.append(uid)
        features.append(feature_item["feature"])
    features = torch.stack(features)  # [n_docs, d_feature]

    # find the closest doc by cosine similarity (dot product)
    scores = torch.matmul(features, query_vec)  # [n_docs]

    if n_return > len(scores):
        n_return = len(scores)
    # return the top n_return of the corresponding uuids
    topk = torch.topk(scores, n_return)
    return {"scores": topk.values.tolist(), "uids": [uuids[i] for i in topk.indices]}

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

