import argparse
from lires.core.encryptClient import generateHexHash
from lires.core.utils import randomAlphaNumeric
from lires.server.auth.account import Account
from lires.server.auth.encryptServer import createAccount, deleteAccount, getHashKeyByName, getAllAccounts

def run():
    parser = argparse.ArgumentParser()
    sp = parser.add_subparsers(dest = "subparser", help = "Key management")

    parser_gen = sp.add_parser("generate", help = "Generate key")
    parser_gen.add_argument("-l", "--length", type = int, default=6, help = "Length of the key")
    parser_gen.add_argument("-i", "--name", default = "Anonymous", help = "Identifier for this key")
    parser_gen.add_argument("-t", "--tags", nargs = "+", default = [], help = "Mandatory tag for this key")
    parser_gen.add_argument("--admin", action="store_true", help = "Set the account to admin")

    parser_reg = sp.add_parser("register", help = "Register key")
    parser_reg.add_argument("key", help = "Key")
    parser_reg.add_argument("-i", "--name", default = "Anonymous", help = "Identifier for this key")
    parser_reg.add_argument("-t", "--tags", nargs = "+", default = [], help = "Mandatory tag for this key")
    parser_reg.add_argument("--admin", action="store_true", help = "Set the account to administrator")

    parser_del = sp.add_parser("delete", help = "Delete key")
    parser_del.add_argument("-i", "--name", help = "Keys with selected name will be deleted")
    parser_del.add_argument("-k", "--key", help = "Key to delete")
    parser_del.add_argument("--hash_key", help = "Hash key to delete")

    parser_lis = sp.add_parser("list", help = "List accounts")
    parser_lis.add_argument("--hashkey", help = "Hash key to show")

    args = parser.parse_args()

    if args.subparser == "generate":
        k = randomAlphaNumeric(args.length)
        res = createAccount(generateHexHash(k), args.name, is_admin = args.admin, mandatory_tags=args.tags)
        if res:
            print("Generated key: ", k)
        else:
            print("Failed")

    elif args.subparser == "register":
        res = createAccount(generateHexHash(args.key), args.name, is_admin = args.admin, mandatory_tags=args.tags)
        if res:
            print("Success")
        else:
            print("Failed")

    elif args.subparser == "delete":
        if args.name is not None:
            hashkeys = getHashKeyByName(args.name)
            print("This action will delete:")
            for hkey in hashkeys:
                print("- ", hkey)
            if input("Continue? (y/[else]): ") == "y":
                for hkey in hashkeys:
                    deleteAccount(hkey)
            else:
                print("Abort")
        else:
            if args.key is not None:
                hexhash = generateHexHash(args.key)
                deleteAccount(hexhash)
            elif args.hash_key is not None:
                hexhash = args.hash_key
                deleteAccount(hexhash)
            else:
                parser_del.print_usage()

    elif args.subparser == "list":
        accounts = getAllAccounts()
        if args.hashkey is not None:
            acc: Account
            acc = accounts[args.hashkey]
            print(acc.detailString())
        else:
            for acc in accounts.values():
                print(acc)

    else:
        parser.print_usage()


if __name__ == "__main__":
    run()