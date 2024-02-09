import argparse
from lires.user import UserPool
from lires.user.encrypt import generateHexHash
from lires.config import USER_DIR
from lires.core.dataTags import DataTags

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
    parser_reg.add_argument("-n", "--name", default = "Anonymous", help = "Identifier for this key, default: Anonymous")
    parser_reg.add_argument( "-t", "--tags", nargs = "+", default = [], help = "Mandatory tag for this key, default: []")
    parser_reg.add_argument("--admin", action="store_true", help = "Set the account to administrator, default: False")

    parser_update = sp.add_parser("update", help = "Update a user")
    parser_update.add_argument("username", help = "Username to update", default=None)
    parser_update.add_argument("-p", "--password", help = "Password to update", default=None)
    parser_update.add_argument("-n", "--name", help = "Name to update", default=None)
    parser_update.add_argument("-t", "--tags", nargs = "+", help = "Mandatory tags to update", default=None)
    parser_update.add_argument("-a", "--admin", help = "Set the account administration (true/false)", default=None, type=str2bool)

    parser_del = sp.add_parser("delete", help = "Delete a user")
    parser_del.add_argument("-u", "--username", help = "Username to delete", default=None)
    parser_del.add_argument("-i", "--id", help = "id to delete", default=None, type=int)

    sp.add_parser("list", help = "List users")

    args = parser.parse_args()

    user_pool = await UserPool().init()
    user_db_conn = user_pool.conn
    try:
        if args.subparser == "add":
            assert args.password is not None, "Password is required"
            await user_db_conn.insertUser(
                username=args.username, password=generateHexHash(args.password), name=args.name,
                is_admin=args.admin, mandatory_tags=DataTags(args.tags).toOrderedList()
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

        elif args.subparser == "delete":
            assert args.username is not None or args.id is not None, "Username or id is required"
            assert not (args.username is not None and args.id is not None), "Cannot specify both username and id"
            if args.username is not None:
                await user_db_conn.deleteUser(args.username)
            if args.id is not None:
                assert args.username is None
                await user_db_conn.deleteUser(args.id)
        
        elif args.subparser == "list":
            for user in await user_pool.all():
                print(await user.toString())

        else:
            parser.print_usage()
        
        await user_db_conn.commit()
    except Exception as e:
        print("Error: ", e)
    finally:
        await user_db_conn.close()

def run():
    import asyncio
    asyncio.run(_run())

if __name__ == "__main__":
    run()