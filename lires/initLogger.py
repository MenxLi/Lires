import logging, sys
from logging.handlers import RotatingFileHandler
from typing import Optional
from .core.utils import BCOLORS
from .confReader import LOG_FILE

def initDefaultLogger(log_level = "INFO") -> logging.Logger:
    """
    Log will be recorded in LOG_FILE
    """
    return setupLogger(
        _logger = "lires",
        term_id = "default",
        term_id_color = BCOLORS.OKGRAY,
        term_log_level=log_level,
        file_path=LOG_FILE,
        file_log_level="DEBUG",
        attach_execption_hook=True
    )

def setupLogger(
        _logger: str | logging.Logger, 
        term_id: Optional[str] = None, 
        term_id_color = BCOLORS.OKGRAY, 
        term_log_level = "INFO",
        file_path: Optional[str] = None,
        file_log_level = "INFO",
        attach_execption_hook = False
        ) -> logging.Logger:
    """
    - term_id: will be used as terminal prefix
    - term_id_color: color of identifier
    - term_log_level: log level of terminal
    - file_path: file to save log
    - file_log_level: log level of save_file
    - attach_execption_hook: whether to redirect unhandled exceptions to the logger
    """
    if term_id is None:
        if isinstance(_logger, str):
            term_id = _logger
        else:
            term_id = _logger.name
    if isinstance(_logger, str):
        logger = logging.getLogger(_logger)
    else:
        logger = _logger

    # remove all other handlers
    logger.handlers.clear()

    # get less critical log level and set it to be the level of logger
    logger.setLevel(min(logging.getLevelName(term_log_level), logging.getLevelName(file_log_level)))

    _ch = logging.StreamHandler()
    _ch.setLevel(term_log_level)
    _ch.setFormatter(logging.Formatter(term_id_color +f'[{term_id}]'+BCOLORS.OKCYAN + \
                                       ' %(asctime)s - %(levelname)s - ' + BCOLORS.ENDC + ' %(message)s'))
    logger.addHandler(_ch)

    if file_path is not None:
        _fh = logging.FileHandler(file_path)
        _fh = RotatingFileHandler(file_path, "a", maxBytes = 1024*1024, backupCount = 1, encoding = "utf-8")
        _fh.setLevel(file_log_level)
        _fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(_fh)
    
    if attach_execption_hook:
        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
            else:
                logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
            # logger.info("Exit.")
            # sys.exit()
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

