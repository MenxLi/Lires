import os, json, warnings
from subprocess import check_output
import typing

join = os.path.join

_VERSION_HISTORIES = [
    ("0.0.1 - Alpha", "Under development"),
    ("0.0.2 - Alpha", "Under development: Added tag related functions"),
    ("0.0.3 - Alpha", "Under development: Internal code structure change"),
    ("0.0.4", "Added search tools, toolbar, and application style"),
    ("0.0.5", "Finished toolbar, bug fix, use setup.py for distribution"),
    ("0.0.6", "Add bibtex template, Bug fix"),
    ("0.0.7", "Using argparse and child process when starting, add window icon")
]
VERSION, DESCRIPEITON = _VERSION_HISTORIES[-1]

_file_path = os.path.abspath(__file__)

CURR_PATH = join(_file_path, os.path.pardir)
CURR_PATH = os.path.abspath(CURR_PATH)
CONF_FILE_PATH = join(CURR_PATH, "conf.json")
ICON_PATH = join(CURR_PATH, "icons")
STYLESHEET_PATH = join(CURR_PATH, "stylesheets")
DOC_PATH = join(CURR_PATH, "docs")
LOG_FILE = join(CURR_PATH, "log.txt")

def getStyleSheets() -> dict:
    global STYLESHEET_PATH
    ss = {
        # "Aqua": join(STYLESHEET_PATH, "Aqua.qss"),
        "Breeze-light": join(STYLESHEET_PATH, "Breeze", "light.qss"),
        "Breeze-dark": join(STYLESHEET_PATH, "Breeze", "dark.qss"),
        "Chenwen1126-qss": join(STYLESHEET_PATH, "chenwen1126-Qss", "css", "qss.css")
    }
    for f_ in os.listdir(STYLESHEET_PATH):
        k = os.path.splitext(f_)[0]
        v = join(STYLESHEET_PATH, f_)
        if os.path.isfile(v):
            ss[k] = v
    ss["<None>"] = ""
    return ss

def getConf():
    global CONF_FILE_PATH, CURR_PATH
    with open(CONF_FILE_PATH) as conf_file:
        conf = json.load(conf_file)
    # Dev
    dev_conf_path = join(CURR_PATH, "conf_dev.json")
    if os.path.exists(dev_conf_path):
        with open(dev_conf_path, "r") as f:
            conf_ = json.load(f)
            for k in conf_.keys():
                conf[k] = conf_[k]
    conf["database"] = os.path.normpath(conf["database"])
    return conf

def saveToConf(**kwargs):
    with open(CONF_FILE_PATH, "r") as conf_file:
        conf_ori = json.load(conf_file)
    for k,v in kwargs.items():
        conf_ori[k] = v
    with open(CONF_FILE_PATH, "w") as conf_file:
        json.dump(conf_ori, conf_file)

if not os.path.exists(getConf()["database"]):
    warnings.warn("Database not exists, default database path is set. \
        The path can be changed in settings or conf.json")
    data_path = join(CURR_PATH, os.pardir)
    data_path = join(data_path, "Database")
    if not os.path.exists(data_path):
        os.mkdir(data_path)
    saveToConf(database=data_path)
