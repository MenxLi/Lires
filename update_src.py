import requests, zipfile, shutil, os, argparse

DOWNLOAD_URL = "http://limengxun.com/files/src/resbibman.zip"
CURR_DIR = os.path.abspath(os.path.realpath(os.path.dirname(__file__)))

def main():

    parser = argparse.ArgumentParser(
        description="Download the newest release version source code of resbibman"
    )
    parser.add_argument("--here", action="store_true", help="download to this directory and overwrite original files")
    parser.add_argument("-y", "--yes", action="store_true", help="do not ask for confirmation")
    args = parser.parse_args()

    dst_dir = CURR_DIR if args.here else os.path.join(CURR_DIR, "resbibman")

    print("=========================")
    lines = [
        "This script will download the newest release version source code of resbibman",
        "Plase use git pull instead if that is avaliable",
    ]
    print("\n".join(lines))
    

    if not os.path.exists(dst_dir):
        if not args.yes:
            ans = input(f"Destination directory ({dst_dir}) not exists, continue? (y/[else])")
            if ans != "y":
                print("abort.")
                return
        os.mkdir(dst_dir)
    else:
        if not args.yes:
            ans = input(f"Will overwrite {dst_dir}, continue? (y/[else])")
            if ans != "y":
                print("abort.")
                return

    print("Downloading...")
    res = requests.get(DOWNLOAD_URL, stream=True)
    zip_path = os.path.join(CURR_DIR, "rbm.zip")
    if res.ok and res.status_code == 200:
        with open(os.path.join(CURR_DIR, "rbm.zip"), "wb") as fp:
            # create a progress bar
            total_length = int(res.headers.get('content-length'))   # type: ignore
            for chunk in res.iter_content(chunk_size=1024):
                if chunk:
                    fp.write(chunk)
                    fp.flush()
                    done = int(50 * fp.tell() / total_length)
                    print("\r[%s%s]" % ('=' * done, ' ' * (50-done)), end="")
            print("\n")
    else:
        print("failed.")
        return

    print("Extracting...")
    with zipfile.ZipFile(zip_path, "r", compression=zipfile.ZIP_DEFLATED) as zp:
        shutil.rmtree(dst_dir)
        zp.extractall(path = dst_dir)
    if os.path.exists(zip_path):
        os.remove(zip_path)
    
    print("Done. (source code saved to: %s)" % dst_dir)


if __name__ == "__main__":
    main()
