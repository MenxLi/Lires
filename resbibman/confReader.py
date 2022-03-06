import os, json

join = os.path.join

_VERSION_HISTORIES = [
    ("0.0.1 - Alpha", "Under development"),
    ("0.0.2 - Alpha", "Under development: Added tag related functions"),
    ("0.0.3 - Alpha", "Under development: Internal code structure change"),
    ("0.0.4", "Added search tools, toolbar, and application style"),
    ("0.1.0", "Finished toolbar, bug fix, use setup.py for distribution"),
    ("0.1.1", "Add bibtex template, Bug fix"),
    ("0.1.2", "Using argparse when starting, add window icon"),
    ("0.1.3", "Added log file"),
    ("0.2.0", "Use table view"),
    ("0.2.1", "Add context menu"),
    ("0.2.2", "Add pending window, support entry without file"),
    ("0.2.3", "Better support for entry without file"),
    ("0.2.4", "Better support for pending window, add pdf preview to pending window"),
    ("0.2.5", "Enable drag-drop in info panel to add file"),
    ("0.2.6", "Context menu, better documentation"),
    ("0.2.7", "Add markdown render window"),
    ("0.2.8", "Add markdown editor syntax highlight (basic)"),
    ("0.2.9", "UI update"),
    ("0.2.10", "Better support for proceedings and better copy citation"),
    ("0.2.11", "Bug fix: not updating file tag; implement open file location in context menu"),
    ("0.2.12", "Add Cover to info panel"),
    ("0.2.13", "Bug fix: update fitz method naming, use integer value resize"),
    ("0.2.14", "Better image insertion, allow copy paste and drag"),
    ("0.2.15", "Add free document option into file selector"),
    ("0.2.16", "Add url/doi into file info panel"),
    ("0.3.0", "Web viewer!"),
    ("0.3.1", "Icon change & update setup.py distribution & argparse update."),
    ("0.3.2", "Frontend add server query."),
    ("0.3.3", "Frontend add banner (reload database, search), UI update, change frontend server to tornado server, \
        start front end and backend with single python cmd argument."),
    ("0.3.4", "Frontend small update. change backend port to 8079"),
    ("0.3.5", "Now can insert no-file entry by cancel in file selection prompt; Add file size to file info"),
    ("0.3.6", "Change resbibman.backend to resbibman.core"),
]
VERSION, DESCRIPEITON = _VERSION_HISTORIES[-1]

_file_path = os.path.abspath(__file__)

# CURR_PATH = join(_file_path, os.path.pardir)
CURR_PATH = os.path.dirname(_file_path)
CURR_PATH = os.path.abspath(CURR_PATH)
CONF_FILE_PATH = join(CURR_PATH, "conf.json")
ICON_PATH = join(CURR_PATH, "icons")
STYLESHEET_PATH = join(CURR_PATH, "stylesheets")
DOC_PATH = join(CURR_PATH, "docs")
LOG_FILE = join(CURR_PATH, "log.txt")
DEFAULT_DATA_PATH = join(CURR_PATH, os.pardir, "Database")

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
    with open(CONF_FILE_PATH, "r", encoding="utf-8") as conf_file:
        conf = json.load(conf_file)
    conf["database"] = os.path.normpath(conf["database"])
    return conf

def getConfV(key : str):
    return getConf()[key]

def saveToConf(**kwargs):
    try:
        with open(CONF_FILE_PATH, "r", encoding="utf-8") as conf_file:
            conf_ori = json.load(conf_file)
    except FileNotFoundError:
        conf_ori = dict()
    for k,v in kwargs.items():
        conf_ori[k] = v
    with open(CONF_FILE_PATH, "w", encoding="utf-8") as conf_file:
        json.dump(conf_ori, conf_file)
