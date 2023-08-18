import os, logging
from lires.confReader import RBM_HOME

RBMSERVER_HOME = os.path.join(RBM_HOME, "RBMWeb")

ACCOUNT_DIR = os.path.join(RBMSERVER_HOME, "accounts")

DISCUSSION_DB_PATH = os.path.join(RBMSERVER_HOME, "discuss.db")
logger_rbm = logging.getLogger("rbm")

_to_create = [RBMSERVER_HOME, ACCOUNT_DIR]
for fpath in _to_create:
    if not os.path.exists(fpath):
        os.mkdir(fpath)
