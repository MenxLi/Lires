import os, logging
from resbibman.confReader import RBM_HOME

CURR_DIR = os.path.abspath(os.path.realpath(os.path.dirname(__file__)))
RBMWEB_HOME = os.path.join(RBM_HOME, "RBMWeb")

ENC_KEY_PATH = os.path.join(RBMWEB_HOME, "key.txt")
DISCUSSION_DB_PATH = os.path.join(RBMWEB_HOME, "discuss.db")
logger_rbm = logging.getLogger("rbm")

_to_create = [RBMWEB_HOME]
for fpath in _to_create:
    if not os.path.exists(fpath):
        os.mkdir(fpath)
