import os, json

CURR_DIR = os.path.abspath(os.path.realpath(os.path.dirname(__file__)))

DATA_DIR = os.path.join(CURR_DIR, "data")
ENC_KEY_PATH = os.path.join(DATA_DIR, "key.txt")

_to_create = [DATA_DIR]
for fpath in _to_create:
    if not os.path.exists(fpath):
        os.mkdir(fpath)

def getRBMWebConf():
    # Change working dir
    file_dir = os.path.dirname(os.path.realpath(__file__))
    # os.chdir(file_dir)

    with open(os.path.join(file_dir, "config.json"), "r", encoding= "utf-8") as fp:
        conf = json.load(fp)
    return conf
