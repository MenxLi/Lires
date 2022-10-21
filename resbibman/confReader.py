import os, json, tempfile, logging
from typing import Tuple, TypedDict, List
from .core import globalVar as G

class _ConfServerPresetT(TypedDict):
    host: str
    port: str
    access_key: str

class _ConfFontSizeT(TypedDict):
    data: Tuple[str, int]
    tag: Tuple[str, int]

class _ConfGUIStatusT(TypedDict):
    show_toolbar: bool

class ResbibmanConfT(TypedDict):
    """
    Refer to rbm-resetconf 
    for the generation of default configuration file
    """
    accepted_extensions: List[str]
    database: str
    # Server settings
    server_preset: List[_ConfServerPresetT]
    host: str
    port: str
    access_key: str
    # Tag settings
    default_tags: List[str]
    sort_method: str
    sort_reverse: bool
    table_headers: List[str]

    font_sizes: _ConfFontSizeT
    stylesheet: str
    auto_save_comments: bool
    gui_status: _ConfGUIStatusT

rbm_logger = logging.getLogger("rbm")

join = os.path.join

WEBPAGE = "https://github.com/MenxLi/ResBibManager"

__this_file_path = os.path.abspath(__file__)

CURR_PATH = os.path.dirname(__this_file_path)
CURR_PATH = os.path.abspath(CURR_PATH)
RBM_HOME = os.path.join(os.path.expanduser("~"), ".RBM")

if G.prog_args and G.prog_args.config_file:
    CONF_FILE_PATH = os.path.abspath(G.prog_args.config_file)
    if os.path.isdir(CONF_FILE_PATH):
        CONF_FILE_PATH = os.path.join(CONF_FILE_PATH, "rbm-conf.json")
else:
    CONF_FILE_PATH = join(RBM_HOME, "conf.json")

ICON_PATH = join(CURR_PATH, "icons")
STYLESHEET_PATH = join(CURR_PATH, "stylesheets")
DOC_PATH = join(CURR_PATH, "docs")
BIB_TEMPLATE_PATH = join(DOC_PATH, "bibtexTemplates")
ASSETS_PATH = join(CURR_PATH, "assets")

DEFAULT_DATA_PATH = join(RBM_HOME, "Database")
LOG_FILE = join(RBM_HOME, "log.txt")

TMP_DIR = os.path.join(RBM_HOME, "RBM.cache")
TMP_DB = os.path.join(TMP_DIR, "Database")      # For online mode
TMP_COVER = os.path.join(TMP_DIR, "cover")      # For cover cache
TMP_WEB = os.path.join(TMP_DIR, "webpage")  # For unzip hpack cache
TMP_WEB_NOTES = os.path.join(TMP_DIR, "notes_webpage")  # For notes as webpages

# Create directories if they don't exist
if not os.path.exists(RBM_HOME):
    os.mkdir(RBM_HOME)
if not os.path.exists(TMP_DIR):
    os.mkdir(TMP_DIR)
for _p in [TMP_DIR, TMP_DB, TMP_COVER, TMP_WEB, TMP_WEB_NOTES]:
    if not os.path.exists(_p):
        os.mkdir(_p)

def getStyleSheets() -> dict:
    global STYLESHEET_PATH
    ss = {
        # "Aqua": join(STYLESHEET_PATH, "Aqua.qss"),
        "Breeze-light": join(STYLESHEET_PATH, "Breeze", "light.qss"),
        "Breeze-dark": join(STYLESHEET_PATH, "Breeze", "dark.qss"),
    }
    for f_ in os.listdir(STYLESHEET_PATH):
        k = os.path.splitext(f_)[0]
        v = join(STYLESHEET_PATH, f_)
        if os.path.isfile(v) and v.endswith(".qss"):
            ss[k] = v
    ss["<None>"] = ""
    return ss

def getConf() -> ResbibmanConfT:
    global CONF_FILE_PATH, CURR_PATH, G
    if not hasattr(G, "config"):
        with open(CONF_FILE_PATH, "r", encoding="utf-8") as conf_file:
            conf: ResbibmanConfT = json.load(conf_file)
            G.config = conf
    else:
        # Save configuration to global buffer
        # To not repeatedly reading configuration file
        conf = G.config
    conf["database"] = os.path.normpath(conf["database"])
    conf["database"] = os.path.realpath(conf["database"])
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

    # Reset global configuration buffer
    # So that next time the configuration will be read from file by getConf/getConfV
    G.resetGlobalConfVar()

def saveToConf_guiStatus(**kwargs):
    gui_status = getConfV("gui_status")
    for k,v in kwargs.items():
        gui_status[k] = v
    saveToConf(gui_status = gui_status)

