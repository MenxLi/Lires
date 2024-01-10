"""
Build search index for the database
"""
import argparse, asyncio

from lires.confReader import DATABASE_DIR, VECTOR_DB_PATH
from lires.core.dataClass import DataBase
from lires.core.textUtils import buildFeatureStorage, queryFeatureIndex, queryFeatureIndexByUID
from lires.utils import MuteEverything
from lires.core import globalVar as G

import tiny_vectordb


def parseArgs() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build search index for the database")
    parser.add_argument("--iserver-host", action="store", type=str, default="127.0.0.1", help="iserver host")
    parser.add_argument("--iserver-port", action="store", type=int, default=8731, help="iserver port")
    subparsers = parser.add_subparsers(dest="subparser", help="sub-command help")

    sp_feat = subparsers.add_parser("build", help="build the index")
    sp_feat.add_argument("--force", action="store_true", help="force-rebuild")
    sp_feat.add_argument("--max-words", action="store", type=int, default=2048, help="max words per document used for summarization, more words will be truncated")
    sp_feat.add_argument("--no-llm-fallback", action="store_true", help="not use LLM as fallback when abstract is not available")

    sp_query = subparsers.add_parser("query", help="query the index")
    sp_query.add_argument("aim", action="store", type=str, help="query string")
    sp_query.add_argument("--n-return", action="store", type=int, default=16, help="number of documents to return")
    sp_query.add_argument("-ou", "--output-uid", action="store_true", help="print uid instead of human-readable result")
    sp_query.add_argument("-iu", "--input-uid", action="store_true", help="input is uid instead of query string, essentially ask for reading the document with the given uid")

    args = parser.parse_args()
    if args.subparser is None:
        parser.print_help()
        exit()
    return args

def main():
    args = parseArgs()
    with MuteEverything():
        db = DataBase().init(DATABASE_DIR)

    # set global variables of iServer
    # so that when initializing iServerConn, it can get the correct host and port
    G.iserver_host = args.iserver_host
    G.iserver_port = args.iserver_port

    if args.subparser == "build":
        vector_db = tiny_vectordb.VectorDatabase(VECTOR_DB_PATH, [{"name": "doc_feature", "dimension": 768}])
        asyncio.run(buildFeatureStorage(db, vector_db, use_llm=not args.no_llm_fallback, force=args.force, max_words_per_doc=args.max_words))

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
