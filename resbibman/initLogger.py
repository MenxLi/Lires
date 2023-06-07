import logging, sys
from .confReader import LOG_FILE
from logging.handlers import RotatingFileHandler

def initLogger(log_level = "INFO") -> logging.Logger:
    """
    Log will be recorded in LOG_FILE
    """
    logger = logging.getLogger("rbm")
    #  logger.setLevel(getattr(logging, log_level))
    logger.setLevel(logging.DEBUG)

    # StreamHandler show user defined log level
    s_handler = logging.StreamHandler(sys.stdout)
    s_handler.setLevel(getattr(logging, log_level))
    fomatter = logging.Formatter('%(asctime)s (%(levelname)s) - %(message)s')
    s_handler.setFormatter(fomatter)
    logger.addHandler(s_handler)

    # FileHandler show DEBUG log level
    f_handler = RotatingFileHandler(LOG_FILE, "a", maxBytes = 1024*1024, backupCount = 1, encoding = "utf-8")
    f_handler.setLevel(logging.DEBUG)
    fomatter = logging.Formatter('%(asctime)s (%(levelname)s) - %(message)s')
    f_handler.setFormatter(fomatter)
    logger.addHandler(f_handler)

    # re-direct stdout and error
    #  sys.stdout = LoggingLogger(logger, logging.INFO, write_to_terminal = False)
    #  sys.stderr = LoggingLogger(logger, logging.ERROR, write_to_terminal = False)
    # re-direct unhandled exceptions
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
        else:
            logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        logger.info("Exit.")
        sys.exit()
    sys.excepthook = handle_exception
    return logger

class LoggingLogger():
    """
    Redirect stream to logging.Logger
    """
    def __init__(self, logger: logging.Logger, level = logging.INFO, write_to_terminal = True):
        self.terminal = sys.stdout
        self.logger = logger
        self.level = level
        self.write_terminal = write_to_terminal
 
    def write(self, message):
        if self.write_terminal:
            self.terminal.write(message)
        if message != "\n":
            self.logger.log(self.level, message)
 
    def flush(self):
        if self.write_terminal:
            self.terminal.flush()

