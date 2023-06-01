"""
Build search index for the database
"""
import argparse, asyncio, os
import torch, tqdm
import openai.error
from resbibman.confReader import TMP_INDEX, getConf
from resbibman.core.dataClass import DataBase
from resbibman.core.pdfTools import PDFAnalyser

from ..lmTools import vectorize, structuredSummerize
from ..lmInterface import StreamIterType
from ..utils import MuteEverything

DOC_FEATURE_PATH = os.path.join(TMP_INDEX, "feature.pt")

def parseArgs() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build search index for the database")
    subparsers = parser.add_subparsers(dest="subparser", help="sub-command help")

    sp_feat = subparsers.add_parser("build", help="build the index")
    sp_feat.add_argument("--force", action="store_true", help="force-rebuild")
    sp_feat.add_argument("--model", action="store", help="model name", default="gpt-3.5-turbo")
    sp_feat.add_argument("--max-words", action="store", type=int, default=512, help="max words per document for summarization")

    sp_query = subparsers.add_parser("query", help="query the index")
    sp_query.add_argument("aim", action="store", type=str, help="query string")
    sp_query.add_argument("--n-return", action="store", type=int, default=16, help="number of documents to return")
    sp_query.add_argument("--uid", action="store_true", help="print uid instead of human-readable result")

    args = parser.parse_args()
    if args.subparser is None:
        parser.print_help()
        exit()
    return args

def buildFeatureIndex(
        db: DataBase, 
        max_words_per_doc: int, 
        model_name: StreamIterType, 
        force = False
        ):
    if os.path.exists(DOC_FEATURE_PATH) and not force:
        feature_dict = torch.load(DOC_FEATURE_PATH)
    else:
        feature_dict = {}

    for idx, (uid, dp) in enumerate(tqdm.tqdm(db.items())):
        if not (dp.is_local and dp.has_file and dp.fm.file_extension == ".pdf"):
            continue
        if uid in feature_dict:
            print(f"Skipping re-build feature index for {dp}")
            continue
        assert dp.file_path is not None  # type hint

        # load pdf
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
        
        if model_name != "":
            # create summary with LLM
            summary = ""
            _summary_title: str = "Title: " + dp.title + "\n"
            print("\n" + _summary_title, end=" ")

            __trail_count = 0
            __max_trail = 3
            while __trail_count < __max_trail and summary == "":
                try:
                    summary = asyncio.run(structuredSummerize(pdf_text, model=model_name, print_func=print))
                    summary = _summary_title + summary
                except openai.error.APIError as e:
                    if __trail_count == __max_trail - 1:
                        print("ERROR: MAX TRAIL REACHED, SKIPPING THIS DOC")
                    print(e)
                    print("OpenAI API error, retrying...")
                    __trail_count += 1
            if summary == "":
                continue
        else:
            # use the original text
            summary = pdf_text

        # featurize the summary
        feature_dict[uid] = asyncio.run(vectorize(summary))[0]  # [d_feature]
    
        # save the feature dict on every 10 document to avoid losing progress
        if idx % 10 == 0:
            torch.save(feature_dict, DOC_FEATURE_PATH)
    torch.save(feature_dict, DOC_FEATURE_PATH)

def queryFeatureIndex(query: str, n_return: int = 10) -> list[str]:
    feature_dict = torch.load(DOC_FEATURE_PATH)

    query_vec = asyncio.run(vectorize(query))[0] # [d_feature]
    # print("Query vector:", query_vec.shape, torch.norm(query_vec))

    # collect uuid and features in to a large buffer
    uuids = []
    features = []
    for uid, vec in feature_dict.items():
        uuids.append(uid)
        features.append(vec)
    features = torch.stack(features)  # [n_docs, d_feature]

    # find the closest doc by cosine similarity (dot product)
    scores = torch.matmul(features, query_vec)  # [n_docs]

    # find the closest doc by euclidean distance
    # scores = -torch.norm(features - query_vec, dim=1)  # [n_docs]

    if n_return > len(scores):
        n_return = len(scores)
    # return the top n_return of the corresponding uuids
    topk = torch.topk(scores, n_return)
    print("Top scores:", topk.values)
    return [uuids[i] for i in topk.indices]


def main():
    args = parseArgs()
    with MuteEverything():
        db_path = getConf()['database']
        db = DataBase().init(db_path, force_offline=True)

    if args.subparser == "build":
        buildFeatureIndex(db, force=args.force, max_words_per_doc=args.max_words, model_name=args.model)

    elif args.subparser == "query":
        res = queryFeatureIndex(args.aim, args.n_return)
        print("-----------------------------------")
        print(f"Query: {args.aim}")
        print("Top results:")
        for i, uid in enumerate(res):
            if args.uid:
                print(f"{uid}")
            else:
                print(f"{i+1}: {db[uid].title}")

    else:
        ...

if __name__ == "__main__":
    main()
