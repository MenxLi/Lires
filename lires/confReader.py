import os, json, logging
from .core import globalVar as G
from .types.configT import *

logger_lrs = logging.getLogger("lires")

join = os.path.join

WEBPAGE = "https://github.com/MenxLi/ResBibManager"

# a schematic ascii image of the file tree
# LRS_HOME
# ├── config.json
# ├── pdf-viewer
# ├── log
# │   ├── core.log
# │   └── server.log
# ├── Database
# │   ├── lrs.db
# │   └── ...
# ├── Users
# │   ├── user.db
# │   └── avatar
# ├── index
# │   ├── vector.db [FEATURE_PATH]
# │   └── summary [DOC_SUMMARY_DIR]
# ├── Lires.cache [TMP_DIR]
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

## Data entries
DATABASE_DIR = join(LRS_HOME, "Database")
USER_DIR = join(LRS_HOME, "Users")
INDEX_DIR = os.path.join(LRS_HOME, "index")      # For index cache

# indexing related
VECTOR_DB_PATH = os.path.join(INDEX_DIR, "vector.db")
DOC_SUMMARY_DIR = os.path.join(INDEX_DIR, "summary")

PDF_VIEWER_DIR = join(LRS_HOME, "pdf-viewer")
LOG_DIR = os.path.join(LRS_HOME, "log")          # For log files
LOG_FILE = join(LRS_HOME, "default.txt")    # may deprecate this

# things under lrs_cache
TMP_DIR = os.path.join(LRS_HOME, "Lires.cache")
TMP_WEB = os.path.join(TMP_DIR, "webpage")  # For unzip hpack cache

ACCEPTED_EXTENSIONS = [".pdf", ".caj", ".html", ".hpack", ".md", ".pptx", ".ppt"]

# Create directories if they don't exist
if not os.path.exists(LRS_HOME):
    os.mkdir(LRS_HOME)
for _p in [TMP_DIR]:
    if not os.path.exists(_p):
        os.mkdir(_p)
for _p in [
    TMP_DIR, TMP_WEB,
    INDEX_DIR, LOG_DIR, DOC_SUMMARY_DIR, 
    ]:
    if not os.path.exists(_p):
        os.mkdir(_p)

def getConf() -> LiresConfT:
    global CONF_FILE_PATH, CURR_PATH, G
    default_config = { }
    if not hasattr(G, "config"):
        with open(CONF_FILE_PATH, "r", encoding="utf-8") as conf_file:
            read_conf = json.load(conf_file)
        conf: LiresConfT = {**default_config, **read_conf}   # type: ignore
        G.config = conf

    # Configuration saved at global buffer
    # To not repeatedly reading/parsing configuration file
    return G.config

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

def generateDefaultConf():
    """
    Generate default configuration file at CONF_FILE_PATH
    """
    default_config: LiresConfT = {
        # jit compile configuration for tiny_vectordb
        'tiny_vectordb_compile_config':{
            'cxx': 'g++',
            'additional_compile_flags': [
                '-march=native',
                '-mtune=native',
            ],
            'additional_link_flags': []
        },

        # TODO: add more fields in the future, 
        # maybe some fields for LLM configurations
    }

    with open(CONF_FILE_PATH, "w", encoding="utf-8") as fp:
        json.dump(default_config, fp, indent=1)
    
    print("Generated default configuration file at: ", CONF_FILE_PATH)
    return 