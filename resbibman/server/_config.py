import os, logging
from resbibman.confReader import RBM_HOME

RBMSERVER_HOME = os.path.join(RBM_HOME, "RBMWeb")

ENC_KEY_PATH = os.path.join(RBMSERVER_HOME, "key.txt")
DISCUSSION_DB_PATH = os.path.join(RBMSERVER_HOME, "discuss.db")
logger_rbm = logging.getLogger("rbm")

_to_create = [RBMSERVER_HOME]
for fpath in _to_create:
    if not os.path.exists(fpath):
        os.mkdir(fpath)
