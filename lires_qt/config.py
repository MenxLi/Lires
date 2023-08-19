import os
from lires.confReader import LRS_HOME

__this_file_path = os.path.abspath(os.path.realpath(__file__))
MODULE_PATH = os.path.abspath(os.path.dirname(__this_file_path))

ICON_PATH = os.path.join(MODULE_PATH, "icons")
DOC_PATH = os.path.join(MODULE_PATH, "docs")
__STYLESHEET_PATH = os.path.join(MODULE_PATH, "stylesheets")

def getStyleSheets() -> dict:
    global __STYLESHEET_PATH
    ss = {
        # "Aqua": join(STYLESHEET_PATH, "Aqua.qss"),
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
