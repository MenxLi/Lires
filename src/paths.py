import os

_file_path = os.path.abspath(__file__)

CURR_PATH = os.path.join(_file_path, os.path.pardir)
CURR_PATH = os.path.abspath(CURR_PATH)

CONF_FILE_PATH = os.path.join(CURR_PATH, "conf.json")
print(CONF_FILE_PATH)

DATA_PATH = os.path.join(CURR_PATH, os.path.pardir)
DATA_PATH = os.path.join(DATA_PATH, "Database")
DATA_PATH = os.path.abspath(DATA_PATH)
print(DATA_PATH)
