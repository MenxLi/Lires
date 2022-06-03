import argparse, os
from ..backend.discussUtils import DiscussDatabase, showDiscuss
from ..backend.confReader import DISCUSSION_DB_PATH


def main():
    _description = "To manage online discussion database"
    parser = argparse.ArgumentParser(description=_description)
    parser.add_argument("-d", "--delete", nargs="+", default=[], help="delete discussion(s)")
    parser.add_argument("-f", "--file", action="store_true", help="select by file")
    parser.add_argument("--reset_database", action="store_true", \
                        help="reset database, will delete all discussions!")

    args = parser.parse_args()

    if args.reset_database:
        if input("This action is going to DELETE ALL discussions, continue? (y/[else])") != "y":
            exit()
        os.remove(DISCUSSION_DB_PATH)
        print("Deleted - ", DISCUSSION_DB_PATH)
        exit()

    database = DiscussDatabase()

    if args.delete:
        to_delete = args.delete
        # Delete by file_uid
        if args.file:
            for file_uid in to_delete:
                database.delDiscussAll(file_uid)
            print("Deleted")
            database.db_con.close()
            exit()
        # Delete by discuss_uid
        for discuss_uid in to_delete:
            line = database[discuss_uid]
            if line is not None:
                print("Deleting...")
                print(showDiscuss(line))
                database.delDiscuss(discuss_uid)
        database.db_con.close()
        exit()




