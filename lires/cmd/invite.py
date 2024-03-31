
import argparse
from lires.loader import initResources

async def _run():
    parser = argparse.ArgumentParser()
    sp = parser.add_subparsers(dest = "subparser", help = "Invitation Key management")

    parser_create = sp.add_parser("create", help = "Create an invitation code")
    parser_create.add_argument("code", help="Invitation code", type = str)
    parser_create.add_argument("-m", "--max-uses", help = "Max uses of this code", default = 1, type = int)

    parser_del = sp.add_parser("delete", help = "Delete an invitation code")
    parser_del.add_argument("code", help="Invitation code", type = str)

    parser_list = sp.add_parser("list", help = "List users")
    parser_list.add_argument("--valid", help = "Only list valid codes", action = "store_true")

    args = parser.parse_args()

    user_pool, db_pool = await initResources()
    user_db_conn = user_pool.conn
    try:
        if args.subparser == "create":
            await user_db_conn.createInvitation(
                code = args.code,
                created_by=0,
                max_uses=args.max_uses,
            )
        
        elif args.subparser == "delete":
            await user_db_conn.deleteInvitation(args.code)

        elif args.subparser == "list":
            for inv in await user_db_conn.listInvitations():
                if not inv["max_uses"] > inv["uses"] and args.valid:
                    continue
                
                print(f"{inv['id']}: {inv['code']} (created by {inv['created_by']}, uses: {inv['uses']}/{inv['max_uses']})")
                    

        else:
            parser.print_usage()
        
        await user_db_conn.commit()
    except Exception as e:
        print("Error: ", e)
    finally:
        await db_pool.close()
        await user_db_conn.close()

def run():
    import asyncio
    asyncio.run(_run())

if __name__ == "__main__":
    run()