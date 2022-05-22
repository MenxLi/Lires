import os, json

CURR_DIR = os.path.abspath(os.path.realpath(os.path.dirname(__file__)))
ENC_KEY_PATH = os.path.join(CURR_DIR, "key.txt")

def getRBMWebConf():
    # Change working dir
    file_dir = os.path.dirname(os.path.realpath(__file__))
    # os.chdir(file_dir)

    with open(os.path.join(file_dir, "config.json"), "r", encoding= "utf-8") as fp:
        conf = json.load(fp)
    return conf