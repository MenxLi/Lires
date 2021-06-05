import os, json, warnings

_versions = [
    ("0.0.1 - Alpha", "Under development"),
    ("0.0.2 - Alpha", "Under development: Added tag related functions")
]
VERSION, DESCRIPEITON = _versions[-1]

_file_path = os.path.abspath(__file__)

CURR_PATH = os.path.join(_file_path, os.path.pardir)
CURR_PATH = os.path.abspath(CURR_PATH)

CONF_FILE_PATH = os.path.join(CURR_PATH, "conf.json")
with open(CONF_FILE_PATH) as conf_file:
    conf = json.load(conf_file)

if not os.path.exists(conf["database"]):
    warnings.warn("Database not exists, default database path is set. \
        The path can be changed in conf.json")
    data_path = os.path.join(CURR_PATH, os.pardir)
    data_path = os.path.join(data_path, "Database")
    if not os.path.exists(data_path):
        os.mkdir(data_path)
    conf["database"] = data_path

def saveToConf(**kwargs):
    for k,v in kwargs.items():
        conf[k] = v
    with open(CONF_FILE_PATH, "w") as conf_file:
        json.dump(conf, conf_file)


