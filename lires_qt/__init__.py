
import os
from lires.initLogger import setupLogger
from lires.confReader import LRS_HOME
from lires.core.utils import BCOLORS

setupLogger(
    "lires",
    term_id="core",
    term_log_level="DEBUG",
    term_id_color=BCOLORS.OKGRAY,
    file_path = os.path.join(LRS_HOME, "core.log"),
    file_log_level="INFO"
    )

setupLogger(
    "lires_qt",
    term_id="gui",
    term_log_level="DEBUG",
    term_id_color=BCOLORS.OKGREEN,
    file_path = os.path.join(LRS_HOME, "gui.log"),
    file_log_level="DEBUG"
    )