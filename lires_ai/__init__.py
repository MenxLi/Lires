"""
Intelligent lires,
AI tools & GPU acceleration
"""


from lires.version import VERSION
from .utils import setupLogger

def initLogger(level = "info"):
    return setupLogger(
        "LiresAI",
        term_id="iserver",
    )

initLogger()