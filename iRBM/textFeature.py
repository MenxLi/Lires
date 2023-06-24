
"""
Depreciated, use resbibman.core.textUtils instead
"""
import os
import asyncio
import tqdm
from typing import TypedDict
import torch
import openai, openai.error
from resbibman.confReader import DOC_FEATURE_PATH
from resbibman.core.dataClass import DataBase, DataPoint
from resbibman.core.pdfTools import getPDFText

from .lmInterface import StreamIterType
from .lmTools import structuredSummerize, featurize

FeatureDict = dict[str, torch.Tensor]
FeatureQueryResult = TypedDict("FeatureQueryResult", {"uids": list[str], "scores": list[float]})
def buildFeatureStorage(
        db: DataBase, 
        max_words_per_doc: int, 
        model_name: StreamIterType, 
        force = False
        ):
    if os.path.exists(DOC_FEATURE_PATH) and not force:
        feature_dict = torch.load(DOC_FEATURE_PATH)
    else:
        feature_dict = {}
    
    def createSummaryWithLLM(text: str, dp: DataPoint):
        summary = ""
        _summary_title: str = "Title: " + dp.title + "\n"
        print("\n" + _summary_title, end=" ")

        __trail_count = 0
        __max_trail = 3
        while __trail_count < __max_trail and summary == "":
            try:
                summary = asyncio.run(structuredSummerize(text, model=model_name, print_func=print))
                summary = _summary_title + summary
            except openai.error.APIError as e:
                if __trail_count == __max_trail - 1:
                    print("ERROR: MAX TRAIL REACHED, SKIPPING THIS DOC WITH ONLY TITLE")
                    summary = _summary_title
                print(e)
                print("OpenAI API error, retrying...")
                __trail_count += 1
        return summary
    
    for idx, (uid, dp) in enumerate(tqdm.tqdm(db.items())):
        if not dp.fm.readAbstract():
            if not (dp.is_local and dp.has_file and dp.fm.file_extension == ".pdf"):
                continue
        if uid in feature_dict:
            print(f"Skipping re-build feature index for {dp}")
            continue
        assert dp.file_path is not None  # type hint

        # load pdf
        doc_path = dp.file_path

        # fallback order: 1. abstract, 2. pdf text
        if dp.fm.readAbstract():
            src_text = dp.fm.readAbstract()
        else:
            src_text = getPDFText(doc_path, max_words_per_doc)
        
        if model_name != "":
            summary = createSummaryWithLLM(src_text, dp)
        else:
            summary = src_text
            if summary == "":
                print("Warning: empty pdf text, use title only: {}".format(dp.title))
                summary = dp.title

        # featurize the summary
        feature_dict[uid] = asyncio.run(featurize(summary, dim_reduce=True))  # [d_feature]
    
        # save the feature dict on every 10 document to avoid losing progress
        if idx % 10 == 0:
            torch.save(feature_dict, DOC_FEATURE_PATH)
    torch.save(feature_dict, DOC_FEATURE_PATH)

def queryFeatureIndex(query: str, n_return: int = 16) -> FeatureQueryResult:
    if os.path.exists(DOC_FEATURE_PATH):
        feature_dict: FeatureDict = torch.load(DOC_FEATURE_PATH)
    else:
        raise FileNotFoundError("Feature index not found, please build the index storage first")
    query_vec = asyncio.run(featurize(query, dim_reduce=True)) # [d_feature]
    if len(feature_dict) == 0:
        raise ValueError("Feature index is empty, please build the index storage first")

    # collect uuid and features in to a large chunk for batch processing
    uuids = []
    features = []
    for uid, vec in feature_dict.items():
        uuids.append(uid)
        features.append(vec)
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

