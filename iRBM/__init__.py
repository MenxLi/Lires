"""
Intelligent resbibman,
AI tools & GPU acceleration
"""


from resbibman.initLogger import setupLogger

def initLogger(level = "info"):
    return setupLogger(
        "iRBM",
        term_id="iserver",
    )

initLogger()