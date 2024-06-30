from ..config import generateDefaultConf, CONF_FILE_PATH
import argparse, json

def run():
    parser = argparse.ArgumentParser(description="Configuration file utilities")
    sp = parser.add_subparsers(dest="subparser")
    sp_reset = sp.add_parser("reset", help="Reset configuration file to default")
    sp_reset.add_argument("-g", "--group", type=str, help="Server ID", default=None)
    sp.add_parser("show", help="Show configuration file")

    sp_edit = sp.add_parser("edit", help="Edit configuration file")
    sp_edit.add_argument("-u", "--use_editor", default="", help="choose editor, e.g. . -u vim will invoke 'vim <config>.json'")

    args = parser.parse_args()
    if args.subparser == "reset":
        generateDefaultConf(args.group)

    elif args.subparser == "show":
        print("Configuration file: ", CONF_FILE_PATH)
        with open(CONF_FILE_PATH, "r", encoding="utf-8") as fp:
            print(json.dumps(json.load(fp), indent=1))

    elif args.subparser == "edit":
        from lires.utils import openFile
        import subprocess
        if args.use_editor:
            subprocess.call([args.use_editor, CONF_FILE_PATH])
        else:
            openFile(CONF_FILE_PATH)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    run()