"""
This is a script to download the newest release version source code of lires,
for those who do not have access to the git repository.
"""
import requests, zipfile, shutil, os, argparse, tempfile

DOWNLOAD_URL = "http://limengxun.com/files/src/lires.zip"
CURR_DIR = os.path.abspath(os.path.realpath(os.path.dirname(__file__)))

def main():

    parser = argparse.ArgumentParser(
        description="Download the newest release version source code of lires"
    )
    parser.add_argument("-d", "--dest", action="store", help="destination directory, default to <this_dir>/lires", default=os.path.join(CURR_DIR, "lires"))
    parser.add_argument("-y", "--yes", action="store_true", help="do not ask for confirmation")
    args = parser.parse_args()

    dst_dir = args.dest
    zip_path = os.path.join(tempfile.gettempdir(), "rbm.zip")

    print("=========================")
    lines = [
        "This script will download the newest release version source code of lires",
        "Plase use git pull instead if that is avaliable",
    ]
    print("\n".join(lines))
    

    if not os.path.exists(dst_dir):
        if not args.yes:
            ans = input(f"Will create {dst_dir}, continue? (y/[else])")
            if ans != "y":
                print("abort.")
                return
        os.mkdir(dst_dir)
    else:
        assert os.path.isdir(dst_dir), f"{dst_dir} is not a directory"
        if not args.yes:
            ans = input(f"Will overwrite {dst_dir}, continue? (y/[else])")
            if ans != "y":
                print("abort.")
                return

    print("Downloading...")
    res = requests.get(DOWNLOAD_URL, stream=True)
    if res.ok and res.status_code == 200:
        with open(zip_path, "wb") as fp:
            # create a progress bar
            total_length = int(res.headers.get('content-length'))   # type: ignore
            for chunk in res.iter_content(chunk_size=1024):
                if chunk:
                    fp.write(chunk)
                    fp.flush()
                    done = int(50 * fp.tell() / total_length)
                    print("\r[%s%s]" % ('=' * done, ' ' * (50-done)), end="")
        print("", end="\n")
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
