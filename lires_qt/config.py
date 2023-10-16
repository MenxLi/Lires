import os, json
from lires.confReader import LRS_HOME
from lires.core import globalVar as G
from typing import TypedDict, List, Tuple
import darkdetect

__this_file_path = os.path.abspath(os.path.realpath(__file__))
MODULE_PATH = os.path.abspath(os.path.dirname(__this_file_path))

ICON_PATH = os.path.join(MODULE_PATH, "icons")
DOC_PATH = os.path.join(MODULE_PATH, "docs")
ASSETS_PATH = os.path.join(MODULE_PATH, "assets")
__STYLESHEET_PATH = os.path.join(ASSETS_PATH, "stylesheets")
BIB_TEMPLATE_PATH = os.path.join(ASSETS_PATH, "bibtexTemplates")

def getStyleSheets() -> dict:
    global __STYLESHEET_PATH
    ss = {
        "Breeze-light": os.path.join(__STYLESHEET_PATH, "Breeze", "light.qss"),
        "Breeze-dark": os.path.join(__STYLESHEET_PATH, "Breeze", "dark.qss"),
    }
    for f_ in os.listdir(__STYLESHEET_PATH):
        k = os.path.splitext(f_)[0]
        v = os.path.join(__STYLESHEET_PATH, f_)
        if os.path.isfile(v) and v.endswith(".qss"):
            ss[k] = v
    ss["<None>"] = ""
    return ss

class _ConfServerPresetT(TypedDict):
    host: str
    port: str
    access_key: str

class _ConfFontSizeT(TypedDict):
    data: Tuple[str, int]
    tag: Tuple[str, int]

class _ConfGUIStatusT(TypedDict):
    show_toolbar: bool
    tag_uncollapsed: List[str]

class LiresGUIConfT(TypedDict):
    """GUI SETTINGS"""
    server_preset: List[_ConfServerPresetT]

    # Tag settings
    default_tags: List[str]

    table_headers: List[str]

    # GUI settings
    sort_method: str
    sort_reverse: bool

    font_sizes: _ConfFontSizeT
    stylesheet: str
    auto_save_comments: bool
    gui_status: _ConfGUIStatusT


__gui_config_file = os.path.join(LRS_HOME, "config_gui.json")
def generateDefaultGUIConfig():
    from .utils import DataTableList
    default_gui_conf: LiresGUIConfT = {
        "server_preset": [],
        "default_tags": [],
		"table_headers" : [ 
				DataTableList.HEADER_FILESTATUS,
				DataTableList.HEADER_TITLE,
				DataTableList.HEADER_YEAR, 
				DataTableList.HEADER_AUTHOR
			 ],
        "sort_method": DataTableList.SORT_TIMEADDED,
        "sort_reverse": False,
        "font_sizes": {
            "data": ["Arial", 10],
            "tag": ["Arial", 10]
        },
        "stylesheet": "Simple-dark" if not darkdetect.isDark() else "Simple",
        "auto_save_comments": False,
        "gui_status": {
            "show_toolbar": True,
            "tag_uncollapsed": []
        },
    }

    with open(__gui_config_file, "w", encoding="utf-8") as fp:
        json.dump(default_gui_conf, fp, indent=1)
    
    print("Generated default GUI configuration file at: ", __gui_config_file)

def getGUIConf() -> LiresGUIConfT:
    try:
        buffer = G.getGlobalAttr("gui_conf")
    except KeyError:
        with open(__gui_config_file, "r", encoding="utf-8") as fp:
            buffer = json.load(fp)
        G.setGlobalAttr("gui_conf", buffer)
    return buffer

def saveToGUIConf(**kwargs):
    with open(__gui_config_file, "r", encoding="utf-8") as fp:
        conf_ori = json.load(fp)
    for k,v in kwargs.items():
        conf_ori[k] = v
    with open(__gui_config_file, "w", encoding="utf-8") as fp:
        json.dump(conf_ori, fp, indent=1)

    if G.hasGlobalAttr("gui_conf"):
        G.deleteGlobalAttr("gui_conf")

# TODO: remove this function
def saveToConf_guiStatus(**kwargs):
    gui_status = getGUIConf()["gui_status"]
    for k,v in kwargs.items():
        gui_status[k] = v
    saveToGUIConf(gui_status = gui_status)