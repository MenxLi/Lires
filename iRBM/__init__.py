"""
Intelligent resbibman,
AI tools & GPU acceleration
"""


import logging
from resbibman.initLogger import setupLogger
from resbibman.confReader import RBM_HOME

def initLogger(level = "info"):
    return setupLogger(
        "iRBM",
        term_id="iserver",
    )

initLogger()