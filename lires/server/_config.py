import os, logging
from lires.confReader import LRS_HOME

LRS_SERVER_HOME = os.path.join(LRS_HOME, "LiresWeb")

ACCOUNT_DIR = os.path.join(LRS_SERVER_HOME, "accounts")

DISCUSSION_DB_PATH = os.path.join(LRS_SERVER_HOME, "discuss.db")
logger_lrs = logging.getLogger("lires")

_to_create = [LRS_SERVER_HOME, ACCOUNT_DIR]
for fpath in _to_create:
    if not os.path.exists(fpath):
        os.mkdir(fpath)
