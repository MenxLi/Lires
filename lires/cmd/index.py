"""
Build search index for the database
"""
import argparse

from lires.core.vecutils import buildFeatureStorage, queryFeatureIndex
from lires.api import IServerConn
from lires.loader import initResources

def parseArgs() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build search index for the database")
    parser.add_argument("user", action="store", type=str, help="user name")
    subparsers = parser.add_subparsers(dest="subparser", help="sub-command help")

    sp_feat = subparsers.add_parser("build", help="build the index")
    sp_feat.add_argument("--force", action="store_true", help="force-rebuild")
    sp_feat.add_argument("--max-words", action="store", type=int, default=2048, help="max words per document used for summarization, more words will be truncated")
    # sp_feat.add_argument("--no-llm-fallback", action="store_true", help="not use LLM as fallback when abstract is not available")

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

async def entry(args):

    user_pool, db_pool = await initResources()
    # check if user exists
    user = await user_pool.getUserByUsername(args.user)
    if user is None:
        print(f"Error: User {args.user} does not exist")
        await user_pool.close(); await db_pool.close()
        exit()
    
    db = await db_pool.get(user)

    iconn = IServerConn()

    if args.subparser == "build":
        vector_db = db.vector
        await buildFeatureStorage(
            iconn, db, vector_db, force=args.force, max_words_per_doc=args.max_words, 
            )

    elif args.subparser == "query":
        vector_collection = await db.vector.getCollection("doc_feature")
        if args.input_uid:
            raise NotImplementedError
        else:
            res = await queryFeatureIndex(
                iconn = iconn,
                vector_collection = vector_collection,
                query = args.aim,
                n_return = args.n_return
                )
        print("-----------------------------------")
        print(f"Query: {args.aim if not args.input_uid else '[' + (await db.get(args.aim)).title + ']'}")
        print("Top results:")
        # for i, (uid, score) in enumerate(zip(res["uids"], res["scores"])):
        #     if args.output_uid:
        #         print(f"{uid}")
        #     else:
        #         print(f"{i+1}: {(await db.get(uid)).title} [score: {score:.4f}]")
        for i, item in enumerate(res):
            uid = item["entry"]["uid"]
            if args.output_uid:
                print(f"{uid}")
            else:
                print(f"{i+1}: {(await db.get(uid)).title} [score: {item['score']:.4f}]")

    else:
        ...
    
    await user_pool.close(); await db_pool.close()

def main():
    import asyncio
    args = parseArgs()
    asyncio.run(entry(args))

if __name__ == "__main__":
    main()