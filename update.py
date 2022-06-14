import requests, zipfile, shutil, os, argparse, json

DOWNLOAD_URL = "http://limengxun.com/files/src/resbibman.zip"
CURR_DIR = os.path.abspath(os.path.realpath(os.path.dirname(__file__)))
CONF_FILE_PATH = os.path.join(CURR_DIR, "resbibman", "conf.json")

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--install", action="store_true")
    parser.add_argument("-r", "--reconfigure", action="store_true")
    args = parser.parse_args()

    print("=========================")
    lines = [
        "This script will download the newest release version source code of resbibman",
        "Plase use git pull instead if that is avaliable",
    ]
    print("\n".join(lines))
    
    if os.path.exists(os.path.join(CURR_DIR, ".git")):
        if input("This is a git repository, download release version will remove .git, continue? (y/[else])") != "y":
            print("abort.")
            return

    print("Downloading...")
    res = requests.get(DOWNLOAD_URL)
    zip_path = os.path.join(CURR_DIR, "rbm.zip")
    if res.ok and res.status_code == 200:
        with open(os.path.join(CURR_DIR, "rbm.zip"), "wb") as fp:
            fp.write(res.content)
    else:
        print("failed.")
        return

    conf = {}       # for syntax checking propose
    if not args.reconfigure:
        with open(CONF_FILE_PATH, "r", encoding="utf-8") as fp:
            conf = json.load(fp)

    print("Extracting...")
    with zipfile.ZipFile(zip_path, "r", compression=zipfile.ZIP_DEFLATED) as zp:
        shutil.rmtree(CURR_DIR)
        zp.extractall(path = CURR_DIR)

        if not args.reconfigure:
            with open(CONF_FILE_PATH, "w", encoding="utf-8") as fp:
                json.dump(conf, fp)

    if args.install:
        print("Installing...")
        os.chdir(CURR_DIR)
        os.system("pip install -e .")
        if args.reconfigure:
            print("Generate default configuration")
            os.system("rbm-resetconf")

if __name__ == "__main__":
    main()
