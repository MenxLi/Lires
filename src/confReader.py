import os, json, warnings
import typing

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


def saveToConf(**kwargs):
    with open(CONF_FILE_PATH, "r") as conf_file:
        conf_ori = json.load(conf_file)
    for k,v in kwargs.items():
        conf_ori[k] = v
    with open(CONF_FILE_PATH, "w") as conf_file:
        json.dump(conf_ori, conf_file)

def creatDataBase() -> typing.List[str]:
    global CURR_PATH
    data_path = os.path.join(CURR_PATH, os.pardir)
    data_path = os.path.join(data_path, "Database")
    if not os.path.exists(data_path):
        os.mkdir(data_path)
    local_data_path = os.path.join(data_path, "local")
    if not os.path.exists(local_data_path):
        os.mkdir(local_data_path)
    remote_data_path = os.path.join(data_path, "remote")
    if not os.path.exists(remote_data_path):
        os.mkdir(remote_data_path)
    return local_data_path, remote_data_path

# Dev
dev_conf_path = os.path.join(CURR_PATH, "conf_dev.json")
if os.path.exists(dev_conf_path):
    with open(dev_conf_path, "r") as f:
        conf_ = json.load(f)
        for k in conf_.keys():
            conf[k] = conf_[k]

if not os.path.exists(conf["database"]):
    warnings.warn("Database not exists, default database path is set. \
        The path can be changed in conf.json")
    conf["database"] = creatDataBase()[0]
if not os.path.exists(conf["database_remote"]):
    warnings.warn("Database(remote) not exists, default database path is set. \
        The path can be changed in conf.json")
    conf["database_remote"] = creatDataBase()[1]

