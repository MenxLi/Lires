import argparse
from lires.loader import initResources
from lires.user.encrypt import generateHexHash
from lires.core.dataTags import DataTags
from lires.utils import tablePrint, TimeUtils

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

async def _run():
    parser = argparse.ArgumentParser()
    sp = parser.add_subparsers(dest = "subparser", help = "Key management")

    parser_reg = sp.add_parser("add", help = "Register a user")
    parser_reg.add_argument("username", help = "Username")
    parser_reg.add_argument("password", help = "Password")
    parser_reg.add_argument("-n", "--name", default = "Anonymous", help = "Identifier for this user, default: Anonymous")
    parser_reg.add_argument("-t", "--tags", nargs = "+", default = [], help = "Mandatory tag for this user, default: []")
    parser_reg.add_argument("-m", "--max-storage", default = None, type = str, help = "Max storage for this user, e.g. 512m, 1g, 1t, defaut: <unset>")
    parser_reg.add_argument("--admin", action="store_true", help = "Set the account to administrator, default: False")

    parser_update = sp.add_parser("update", help = "Update a user")
    parser_update.add_argument("username", help = "Username to update", default=None)
    parser_update.add_argument("-p", "--password", help = "Password to update", default=None)
    parser_update.add_argument("-n", "--name", help = "Name to update", default=None)
    parser_update.add_argument("-t", "--tags", nargs = "+", help = "Mandatory tags to update", default=None)
    parser_update.add_argument("-m", "--max-storage", help = "Max storage to update, e.g. 512m, 1g", default=None, type=str)
    parser_update.add_argument("-a", "--admin", help = "Set the account administration (true/false)", default=None, type=str2bool)

    parser_del = sp.add_parser("delete", help = "Delete a user")
    parser_del.add_argument("-u", "--username", help = "Username to delete", default=None)
    parser_del.add_argument("-i", "--id", help = "id to delete", default=None, type=int)
    parser_del.add_argument("-y", "--yes", help = "Skip confirmation", action="store_true")

    parser_list = sp.add_parser("list", help = "List users")
    parser_list.add_argument("--order", help = "Order by (id, last-active, ...)", default="id", type=str.lower)
    parser_list.add_argument("-t", "--table", help = "Print in table format", action="store_true")
    parser_list.add_argument('-r', "--reverse", help = "Reverse order", action="store_true")
    parser_list.add_argument('--ascii', help = "Only print ascii characters, work only with table", action="store_true")

    def parseStorage(s: str) -> int:
        assert s[:-1].isdigit(), "Invalid storage size"
        assert s[-1].lower() in ["m", "g", "t"], "Invalid storage unit"
        if s[-1].lower() == "m":
            return int(s[:-1]) * 1024 * 1024
        if s[-1].lower() == "g":
            return int(s[:-1]) * 1024 * 1024 * 1024
        if s[-1].lower() == "t":
            return int(s[:-1]) * 1024 * 1024 * 1024 * 1024
        return int(s)

    args = parser.parse_args()

    user_pool, db_pool = await initResources()
    user_db_conn = user_pool.conn
    try:
        if args.subparser == "add":
            assert args.password is not None, "Password is required"
            await user_db_conn.insertUser(
                username=args.username, password=generateHexHash(args.password), name=args.name,
                is_admin=args.admin, mandatory_tags=DataTags(args.tags).toOrderedList(), 
                max_storage=parseStorage(args.max_storage) if args.max_storage is not None else None
            )
        
        elif args.subparser == "update":
            assert args.username is not None, "Username is required"
            user_id = (await user_db_conn.getUser(args.username))["id"]
            if args.password is not None:
                await user_db_conn.updateUser(user_id, password=generateHexHash(args.password))
            if args.name is not None:
                await user_db_conn.updateUser(user_id, name=args.name)
            if args.tags is not None:
                await user_db_conn.updateUser(user_id, mandatory_tags=DataTags(args.tags).toOrderedList())
            if args.admin is not None:
                await user_db_conn.updateUser(user_id, is_admin=args.admin)
            if args.max_storage is not None:
                await user_db_conn.updateUser(user_id, max_storage=parseStorage(args.max_storage))

        elif args.subparser == "delete":
            assert args.username is not None or args.id is not None, "Username or id is required"
            assert not (args.username is not None and args.id is not None), "Cannot specify both username and id"
            if args.username is not None:
                assert args.id is None
                user = await user_pool.getUserByUsername(args.username)
            else:
                assert args.id is not None
                assert args.username is None
                user = await user_pool.getUserById(args.id)
            if user is None:
                print(f"Error: User does not exist")
                return
            if not args.yes:
                if input(f"Are you sure you want to delete user **{await user.toString()}**, "
                         "together with all data associated? (y/[n])").lower() != "y":
                    print("Cancelled.")
                    return
            await db_pool.deleteDatabasePermanently(user.id)
            await user_pool.deleteUserPermanently(user.id)
            print("User deleted.")
        
        elif args.subparser == "list":
            all_users = await user_pool.all()
            sort_key = args.order.replace("-", "_")
            sort_val = [(await user.info())[sort_key] for user in all_users]
            all_users = [user for _, user in sorted(
                zip(sort_val, all_users), key=lambda x: x[0], 
                reverse = args.reverse)
                ]
            def formatascii(s):
                return s.encode('ascii', 'replace').decode()
            if args.table:
                tablePrint(
                    ["ID", "Username", "Name", "Admin", "Mandatory Tags", "Max Storage", "Last Active"],
                    [[
                        (user_info:=(await user.info()))["id"],
                        user_info["username"], 
                        user_info["name"] if not args.ascii else formatascii(user_info["name"]),
                        'X' if user_info["is_admin"] else ' ',
                        '; '.join(user_info["mandatory_tags"]),
                        f"{(user_info['max_storage'])/1024/1024:.1f} MB",
                        TimeUtils.stamp2Local(user_info["last_active"]).strftime("%Y-%m-%d %H:%M:%S")
                    ] for user in all_users]
                )
            else:
                for user in all_users:
                    print(await user.toString())

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