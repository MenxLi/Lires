"""
Intelligent lires,
AI tools & GPU acceleration
"""


from lires.initLogger import setupLogger

def initLogger(level = "info"):
    return setupLogger(
        "iRBM",
        term_id="iserver",
    )

initLogger()