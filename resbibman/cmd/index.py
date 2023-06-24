"""
Build search index for the database
"""
import argparse

from resbibman.confReader import DOC_FEATURE_PATH, getConf
from resbibman.core.dataClass import DataBase
from resbibman.core.textUtils import buildFeatureStorage, queryFeatureIndex, queryFeatureIndexByUID
from resbibman.core.utils import MuteEverything


def parseArgs() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build search index for the database")
    subparsers = parser.add_subparsers(dest="subparser", help="sub-command help")

    sp_feat = subparsers.add_parser("build", help="build the index")
    sp_feat.add_argument("--force", action="store_true", help="force-rebuild")
    sp_feat.add_argument("--max-words", action="store", type=int, default=2048, help="max words per document used for summarization, more words will be truncated")

    sp_query = subparsers.add_parser("query", help="query the index")
    sp_query.add_argument("aim", action="store", type=str, help="query string")
    sp_query.add_argument("--n-return", action="store", type=int, default=16, help="number of documents to return")
    sp_query.add_argument("-ou", "--output_uid", action="store_true", help="print uid instead of human-readable result")
    sp_query.add_argument("-iu", "--input_uid", action="store_true", help="input is uid instead of query string, essentially ask for reading the document with the given uid")

    args = parser.parse_args()
    if args.subparser is None:
        parser.print_help()
        exit()
    return args

def main():
    args = parseArgs()
    with MuteEverything():
        db_path = getConf()['database']
        db = DataBase().init(db_path, force_offline=True)

    if args.subparser == "build":
        buildFeatureStorage(db, force=args.force, max_words_per_doc=args.max_words)

    elif args.subparser == "query":
        if args.input_uid:
            res = queryFeatureIndexByUID(db, args.aim, args.n_return)
        else:
            res = queryFeatureIndex(args.aim, args.n_return)
        print("-----------------------------------")
        print(f"Query: {args.aim if not args.input_uid else '[' + db[args.aim].title + ']'}")
        print("Top results:")
        for i, (uid, score) in enumerate(zip(res["uids"], res["scores"])):
            if args.output_uid:
                print(f"{uid}")
            else:
                print(f"{i+1}: {db[uid].title} [score: {score:.4f}]")

    else:
        ...

if __name__ == "__main__":
    main()
