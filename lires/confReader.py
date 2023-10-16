import os, json, tempfile, logging
from .core import globalVar as G
from .types.configT import *
import deprecated

logger_lrs = logging.getLogger("lires")

join = os.path.join

WEBPAGE = "https://github.com/MenxLi/ResBibManager"

# a schematic ascii image of the file tree
# LRS_HOME
# ├── config.json
# ├── pdf-viewer
# ├── log.txt
# ├── Database (default)
# │   ├── lrs.db
# │   └── ...
# ├── index [INDEX_DIR]
# │   ├── vector.db [FEATURE_PATH]
# │   └── summary [DOC_SUMMARY_DIR]
# ├── Lires.cache [TMP_DIR]
# │   ├── Database [TMP_DB]
# │   ├── cover [TMP_COVER]
# │   ├── webpage [TMP_WEB]
# │   └── notes_webpage [TMP_WEB_NOTES]

__this_file_path = os.path.abspath(os.path.realpath(__file__))

CURR_PATH = os.path.abspath(os.path.dirname(__this_file_path))
if "LRS_HOME" in os.environ:
    LRS_HOME = os.environ["LRS_HOME"]
else:
    LRS_HOME = os.path.join(os.path.expanduser("~"), ".Lires")

if G.prog_args and G.prog_args.config_file:
    CONF_FILE_PATH = os.path.abspath(G.prog_args.config_file)
    if os.path.isdir(CONF_FILE_PATH):
        CONF_FILE_PATH = os.path.join(CONF_FILE_PATH, "lrs-config.json")
else:
    CONF_FILE_PATH = join(LRS_HOME, "config.json")

ASSETS_PATH = join(CURR_PATH, "assets")
BIB_TEMPLATE_PATH = join(ASSETS_PATH, "bibtexTemplates")

DEFAULT_DATA_PATH = join(LRS_HOME, "Database")
DEFAULT_PDF_VIEWER_DIR = join(LRS_HOME, "pdf-viewer")
LOG_FILE = join(LRS_HOME, "log.txt")

INDEX_DIR = os.path.join(LRS_HOME, "index")      # For index cache

# things under lrs_cache
TMP_DIR = os.path.join(LRS_HOME, "Lires.cache")
TMP_DB = os.path.join(TMP_DIR, "Database")      # For online mode
TMP_COVER = os.path.join(TMP_DIR, "cover")      # For cover cache
TMP_WEB = os.path.join(TMP_DIR, "webpage")  # For unzip hpack cache
TMP_WEB_NOTES = os.path.join(TMP_DIR, "notes_webpage")  # For notes as webpages

# indexing related
VECTOR_DB_PATH = os.path.join(INDEX_DIR, "vector.db")
DOC_SUMMARY_DIR = os.path.join(INDEX_DIR, "summary")

# Create directories if they don't exist
if not os.path.exists(LRS_HOME):
    os.mkdir(LRS_HOME)
for _p in [TMP_DIR]:
    if not os.path.exists(_p):
        os.mkdir(_p)
for _p in [TMP_DIR, TMP_DB, TMP_COVER, TMP_WEB, TMP_WEB_NOTES, INDEX_DIR, DOC_SUMMARY_DIR]:
    if not os.path.exists(_p):
        os.mkdir(_p)

def getConf() -> LiresConfT:
    global CONF_FILE_PATH, CURR_PATH, G
    if not hasattr(G, "config"):
        with open(CONF_FILE_PATH, "r", encoding="utf-8") as conf_file:
            conf: LiresConfT = json.load(conf_file)
            G.config = conf
    else:
        # Save configuration to global buffer
        # To not repeatedly reading configuration file
        conf = G.config
    conf["database"] = os.path.normpath(conf["database"])
    conf["database"] = os.path.realpath(conf["database"])
    return conf

def getDatabase(offline: Optional[bool] = None) -> str:
    if offline is None:
        if getConf()["host"]:
            return TMP_DB
        else:
            return getConf()["database"]
    if isinstance(offline, bool):
        if offline:
            return getConf()["database"]
        else:
            return TMP_DB
    else:
        raise TypeError("offline should be bool or None")

def getDatabasePath_withFallback(offline: Optional[bool] = None, fallback: str = os.path.join(LRS_HOME, "Database")) -> str:
    """
    get the path to the database,
    if it not exists, return the default path
    """
    tempt = getDatabase(offline)
    if os.path.exists(tempt):
        return tempt
    else:
        return fallback

@deprecated.deprecated(version="1.2.0", reason="use getConf instead")
def getConfV(key : str):
    try:
        return getConf()[key]
    except json.decoder.JSONDecodeError as e:
        logger_lrs.warn("Error while reading configuration: {}".format(e))
        with open(CONF_FILE_PATH, "r") as fp:
            logger_lrs.debug("Current configuration file: \n{}".format(fp.read()))
        raise Exception("Manual exception, check log.")

def getServerURL() -> str:
    conf = getConf()
    host = conf["host"]
    port = conf["port"]
    if not host:
        return ""
    else:
        return f"{host}:{port}"

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
