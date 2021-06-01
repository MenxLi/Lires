import os, json, warnings

_file_path = os.path.abspath(__file__)

CURR_PATH = os.path.join(_file_path, os.path.pardir)
CURR_PATH = os.path.abspath(CURR_PATH)

CONF_FILE_PATH = os.path.join(CURR_PATH, "conf.json")
with open(CONF_FILE_PATH) as conf_file:
    conf = json.load(conf_file)

if not os.path.exists(conf["database"]):
    warnings.warn("Database not exists, may lead to exceptions.\n\
        Please change settings in the configuration file")
# DATA_PATH = os.path.join(CURR_PATH, os.path.pardir)
# DATA_PATH = os.path.join(DATA_PATH, "Database")
# DATA_PATH = os.path.abspath(DATA_PATH)
# if not os.path.exists(DATA_PATH):
    # os.mkdir(DATA_PATH)
    # print("Database directory created: ", DATA_PATH)
# else:
    # print("Database directory: ", DATA_PATH)
