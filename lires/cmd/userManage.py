import argparse
from lires.core.encryptClient import generateHexHash
from lires.core.utils import randomAlphaNumeric
from lires.user import UsrDBConnection, UserPool
from lires.confReader import USER_DIR

def run():
    parser = argparse.ArgumentParser()
    sp = parser.add_subparsers(dest = "subparser", help = "Key management")

    parser_reg = sp.add_parser("add", help = "Register a user")
    parser_reg.add_argument("username", help = "Username")
    parser_reg.add_argument("password", help = "Password")
    parser_reg.add_argument("-n", "--name", default = "Anonymous", help = "Identifier for this key, default: Anonymous")
    parser_reg.add_argument( "-t", "--tags", nargs = "+", default = [], help = "Mandatory tag for this key, default: []")
    parser_reg.add_argument("--admin", action="store_true", help = "Set the account to administrator, default: False")

    parser_del = sp.add_parser("delete", help = "Delete a user")
    parser_del.add_argument("-u", "--username", help = "Username to delete", default=None)
    parser_del.add_argument("-i", "--id", help = "id to delete", default=None, type=int)

    sp.add_parser("list", help = "List users")

    args = parser.parse_args()

    if args.subparser == "add":
        assert args.password is not None, "Password is required"
        user_db_conn = UsrDBConnection(USER_DIR)
        user_db_conn.insertUser(
            username=args.username, password=args.password, name=args.name,
            is_admin=args.admin, mandatory_tags=args.tags
        )

    elif args.subparser == "delete":
        user_db_conn = UsrDBConnection(USER_DIR)
        assert args.username is not None or args.id is not None, "Username or id is required"
        assert not (args.username is not None and args.id is not None), "Cannot specify both username and id"
        if args.username is not None:
            user_db_conn.deleteUser(args.username)
        if args.id is not None:
            assert args.username is None
            user_db_conn.deleteUser(args.id)
    
    elif args.subparser == "list":
        user_pool = UserPool()
        for user in user_pool:
            print(user)

    else:
        parser.print_usage()


if __name__ == "__main__":
    run()