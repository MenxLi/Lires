"""
Build search index for the database
"""
import argparse, asyncio, os
import torch, tqdm
import openai.error
from resbibman.confReader import TMP_INDEX, getConf
from resbibman.core.dataClass import DataBase
from resbibman.core.pdfTools import PDFAnalyser

from ..lmTools import featurize, structuredSummerize
from ..utils import MuteEverything

DOC_FEATURE_PATH = os.path.join(TMP_INDEX, "feature.pt")

def parseArgs() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build search index for the database")
    subparsers = parser.add_subparsers(dest="subparsers", help="sub-command help")

    sp_feat = subparsers.add_parser("feature", help="Document feature index")
    sp_feat.add_argument("--build", action="store_true", help="build the index")
    sp_feat.add_argument("--query", action="store", help="query the index by a string", default=None)

    args = parser.parse_args()
    return args

def buildFeatureIndex(db: DataBase, max_words_per_doc: int = 512, force = False):
    if os.path.exists(DOC_FEATURE_PATH) and not force:
        feature_dict = torch.load(DOC_FEATURE_PATH)
    else:
        feature_dict = {}

    for uid, dp in tqdm.tqdm(db.items()):
        if not (dp.is_local and dp.has_file and dp.fm.file_extension == ".pdf"):
            continue
        if uid in feature_dict:
            print(f"Skipping re-build feature index for {dp}")
            continue
        assert dp.file_path is not None  # type hint
        doc_path = dp.file_path
        with PDFAnalyser(doc_path) as doc:
            MAX_WORDS = 8192
            pdf_text = doc.getText()
            if len(pdf_text.split()) > MAX_WORDS:
                # too long, truncate
                pdf_text = " ".join(pdf_text.split()[:MAX_WORDS])
            if len(pdf_text.split()) == 0:
                # empty pdf
                continue
        if len(pdf_text.split()) > max_words_per_doc:
            pdf_text = " ".join(pdf_text.split()[:max_words_per_doc])
        

        summary = ""
        _summary_title: str = "Title: " + dp.title + "\n"
        print("\n" + _summary_title, end=" ")

        __trail_count = 0
        __max_trail = 3
        while __trail_count < __max_trail and summary == "":
            try:
                summary = asyncio.run(structuredSummerize(pdf_text, model="vicuna-13b", print_func=print))
                summary = _summary_title + summary
            except openai.error.APIError as e:
                if __trail_count == __max_trail - 1:
                    print("ERROR: MAX TRAIL REACHED, SKIPPING THIS DOC")
                print(e)
                print("OpenAI API error, retrying...")
                __trail_count += 1

        feature_dict[uid] = asyncio.run(featurize(summary, dim_reduct=True))  # [d_feature]
        # break
    
        # save the feature dict on every document...
        torch.save(feature_dict, DOC_FEATURE_PATH)

def queryFeatureIndex(query: str, n_return: int = 10) -> list[str]:
    feature_dict = torch.load(DOC_FEATURE_PATH)

    query_vec = asyncio.run(featurize(query, dim_reduct=True))

    # collect uuid and features in to a large buffer
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
    return [uuids[i] for i in topk.indices]



def main():
    args = parseArgs()
    with MuteEverything():
        db_path = getConf()['database']
        db = DataBase().init(db_path, force_offline=True)

    if args.subparsers == "feature":
        if args.build:
            buildFeatureIndex(db)
        elif args.query is not None:
            n_ret = 16
            res = queryFeatureIndex(args.query, n_ret)
            for i, uid in enumerate(res):
                print(f"Top {i+1}: {db[uid].title}")
        else:
            print("No action specified")

if __name__ == "__main__":
    main()
