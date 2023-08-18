"""
Intelligent lires,
AI tools & GPU acceleration
"""


from lires.initLogger import setupLogger

def initLogger(level = "info"):
    return setupLogger(
        "iLires",
        term_id="iserver",
    )

initLogger()