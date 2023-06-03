"""
Intelligent resbibman,
AI tools & GPU acceleration
"""


import logging

def initLogger(level = "info"):
    if level == "info":
        level = logging.INFO
    elif level == "debug":
        level = logging.DEBUG
    elif level == "warning":
        level = logging.WARNING
    elif level == "error":
        level = logging.ERROR
    else:
        raise ValueError("Unknown log level: %s" % level)

    # get logger
    logger = logging.getLogger("iRBM")
    # set logger
    logger.setLevel(level)
    # set formatter
    formatter = logging.Formatter(
        "[%(levelname)s] %(message)s",
        )
    # set handler
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    # add handler
    logger.addHandler(handler)

initLogger()