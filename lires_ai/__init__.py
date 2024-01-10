"""
Intelligent lires,
AI tools & GPU acceleration
"""


from lires.utils import setupLogger

def initLogger(level = "INFO"):
    level = level.upper()
    return setupLogger(
        "LiresAI",
        term_id="iserver",
        term_log_level=level,
        file_log_level=level,   # type: ignore
    )

initLogger()