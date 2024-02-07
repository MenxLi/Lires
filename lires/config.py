import os, json, logging
from typing import Optional
from .types.configT import *

__logger = logging.getLogger("default")

join = os.path.join

WEBPAGE = "https://github.com/MenxLi/Lires"

# a schematic ascii image of the file tree
# LRS_HOME
# ├── config.json
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
# │   └── ...

if "LRS_HOME" in os.environ:
    LRS_HOME = os.environ["LRS_HOME"]
else:
    LRS_HOME = os.path.join(os.path.expanduser("~"), ".Lires")

CONF_FILE_PATH = join(LRS_HOME, "config.json")

## Data entries
DATABASE_DIR = join(LRS_HOME, "Database")
USER_DIR = join(LRS_HOME, "Users")
INDEX_DIR = os.path.join(LRS_HOME, "index")      # For index cache

# indexing related
VECTOR_DB_PATH = os.path.join(INDEX_DIR, "vector.db")
DOC_SUMMARY_DIR = os.path.join(INDEX_DIR, "summary")

# for log files
LOG_DIR = os.path.join(LRS_HOME, "log")

# things under lrs_cache
TMP_DIR = os.path.join(LRS_HOME, "Lires.cache")

ACCEPTED_EXTENSIONS = [".pdf", '.html']

# Create directories if they don't exist
if not os.path.exists(LRS_HOME):
    os.mkdir(LRS_HOME)
for _p in [TMP_DIR]:
    if not os.path.exists(_p):
        os.mkdir(_p)
for _p in [
    TMP_DIR, INDEX_DIR, LOG_DIR, DOC_SUMMARY_DIR, 
    ]:
    if not os.path.exists(_p):
        os.mkdir(_p)

# Set the default configuration here, 
# will be used for setting default configuration.
# Also for backward compatibility, 
# if the old config file exists, and does not contain some new fields,
# the new fields will be added on top of the old config file on getConf()
import tiny_vectordb
import uuid
__default_config: LiresConfT = {
    'database_id': uuid.uuid4().hex,
    'service_port_range': [21000, 22000],
    'tiny_vectordb_compile_config': tiny_vectordb.autoCompileConfig(),
}
__g_config: Optional[LiresConfT] = None     # buffer
def getConf() -> LiresConfT:
    global __g_config, CONF_FILE_PATH
    if __g_config is None:
        with open(CONF_FILE_PATH, "r", encoding="utf-8") as conf_file:
            read_conf = json.load(conf_file)
        
        # compare the keys and value types recursively
        # TODO: may be replaced by a more elegant solution
        def compareObject(d1, d2):
            if not type(d1) == type(d2):
                __logger.debug(f"Type mismatch: {type(d1)} != {type(d2)}")
                return False
            if isinstance(d1, dict):
                assert isinstance(d2, dict)
                if not len(d1) == len(d2):
                    __logger.debug(f"Dict length mismatch: {d1.keys()} != {d2.keys()}")
                    return False
                for k in d1:
                    if not k in d2:
                        __logger.debug(f"Key mismatch: {d1.keys()} != {d2.keys()}")
                        return False
                for k in d1:
                    if not compareObject(d1[k], d2[k]):
                        return False
            return True
        # warn if the configuration file is outdated
        if not compareObject(read_conf, __default_config):
            __logger.warn("Configuration file outdated, "
            "default configuration will be used as fallback, if errors occur, "
            "please run `lrs-reset` to update the configuration file")

        # merge the default configuration and the configuration file
        conf: LiresConfT = {**__default_config, **read_conf}   # type: ignore

        # eligibility check
        assert len(conf["service_port_range"]) == 2 and \
            conf["service_port_range"][0] < conf["service_port_range"][1], \
            "Invalid service port range: {}".format(conf["service_port_range"])
        assert conf["database_id"].replace("_", "").isalnum(), \
            "Invalid database id: {}".format(conf["database_id"]) + ", must be alphanumeric or underscore"
        
        __g_config = conf

    # Configuration saved at global buffer
    # To not repeatedly reading/parsing configuration file
    return __g_config

def saveToConf(**kwargs):
    global __g_config
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
    # So that next time the configuration will be read from file by getConf
    __g_config = None

def generateDefaultConf():
    """
    Generate default configuration file at CONF_FILE_PATH
    """
    default_config: LiresConfT = __default_config

    with open(CONF_FILE_PATH, "w", encoding="utf-8") as fp:
        json.dump(default_config, fp, indent=1)
    
    print("Generated default configuration file at: ", CONF_FILE_PATH)
    return 