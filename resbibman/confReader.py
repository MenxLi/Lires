import os, json, tempfile, logging
rbm_logger = logging.getLogger("rbm")

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
    ("0.3.3", "Frontend add banner (reload database, search), UI update, change frontend server to tornado server, "\
        "start front end and backend with single python cmd argument."),
    ("0.3.4", "Frontend small update. change backend port to 8079"),
    ("0.3.5", "Now can insert no-file entry by cancel in file selection prompt; Add file size to file info"),
    ("0.3.6", "API update: Change resbibman.backend to resbibman.core"),
    ("0.3.7", "Bug fix: edit weburl or switch mdTab would lead to crash when no file is selected"),
    ("0.3.8", "Use one server to start front and backend"),
    ("0.3.9", "Check if file exists, while adding; change cloud icon"),
    ("0.3.10", "Asynchronous comment saving; use logger instead of print"),
    ("0.3.11", "Allow bibtex editing"),
    ("0.3.12", "More bibtex template"),
    ("0.3.13", "Not automatically save comment, show comment save indicator on info panel; reset_conf option in CLI"),
    ("0.4.0", "Offline html support"),
    ("0.4.1", "Panel collapse buttons; Markdown highlight improvements; UI changes; Minor bug fixes"),
    ("0.5.0", "Online mode!!"),
    ("0.5.1", "Synchronize strategy update; GUI host settings; PDF cover cache; Move some window to dialog class; Clear cache CLI"),
    ("0.5.2", "Asynchronous UI update when connection; Improved watch file changes; Bug fix: basename now not allowed to have question mark"),
    ("0.5.3", "Better file modification monitering; Bug fix: rename/delete tag now will affact unasynchronized data; CLI change"),
    ("0.5.4", "Document update; Use asyncio to accelerate dataloading; Add delete to context menu of file selector; "\
        "CLI update; Bug fixs: rbmweb can serve packed webpages with style, server can serve empty database"),
    ("0.6.0", "Online discussion avaliable; Info file record time as floating time stamp; Key login required for accessing webpage; "\
        "rbm-collect/rbm-discuss; Server can serve notes in html format"),
    ("0.6.0a", "Using PyQt6! View comment preview in online mode"),
    ("0.6.1", "Comment CSS update; Full screen; Bug fixes"),
    ("0.6.2", "Propmt conflict resolving when synchroning; Bug fixes: Now, delete old temp_db when server change, invalid bibtex input won't crash the program, etc."),
    ("0.6.3", "Better logging in log file; Stricter frontend access key requirements; Added update script"),
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
BIB_TEMPLATE_PATH = join(DOC_PATH, "bibtexTemplates")
LOG_FILE = join(CURR_PATH, "log.txt")
ASSETS_PATH = join(CURR_PATH, "assets")
DEFAULT_DATA_PATH = join(CURR_PATH, os.pardir, "Database")

TMP_DIR = tempfile.gettempdir()
TMP_DIR = os.path.join(TMP_DIR, "ResBibMan")
TMP_DB = os.path.join(TMP_DIR, "Database")      # For online mode
TMP_COVER = os.path.join(TMP_DIR, "cover")      # For cover cache
TMP_WEB = os.path.join(TMP_DIR, "webpage")  # For unzip hpack cache
TMP_WEB_NOTES = os.path.join(TMP_DIR, "notes_webpage")  # For notes as webpages

for _p in [TMP_DIR, TMP_DB, TMP_COVER, TMP_WEB, TMP_WEB_NOTES]:
    if not os.path.exists(_p):
        os.mkdir(_p)


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

def getDatabase(offline: bool):
    if offline:
        return getConf()["database"]
    else:
        return TMP_DB

def getConfV(key : str):
    try:
        return getConf()[key]
    except json.decoder.JSONDecodeError as e:
        rbm_logger.warn("Error while reading configuration: {}".format(e))
        with open(CONF_FILE_PATH, "r") as fp:
            rbm_logger.debug("Current configuration file: \n{}".format(fp.read()))
        raise Exception("Manual exception, check log.")

def getServerURL() -> str:
    conf = getConf()
    host = conf["host"]
    port = conf["port"]
    if not host:
        return ""
    else:
        return f"http://{host}:{port}"

def saveToConf(**kwargs):
    try:
        with open(CONF_FILE_PATH, "r", encoding="utf-8") as conf_file:
            conf_ori = json.load(conf_file)
    except FileNotFoundError:
        conf_ori = dict()
    for k,v in kwargs.items():
        conf_ori[k] = v
    with open(CONF_FILE_PATH, "w", encoding="utf-8") as conf_file:
        json.dump(conf_ori, conf_file, indent=1)
