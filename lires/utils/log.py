import logging, sys
from logging.handlers import RotatingFileHandler
from io import TextIOWrapper
from functools import wraps
from typing import Optional, Literal
from lires.confReader import LOG_FILE

from .term import BCOLORS
from .time import TimeUtils

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
        file_log_level="_ALL",
        attach_execption_hook=True
    )

_FileLogLevelT = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "_ALL"]
def setupLogger(
        _logger: str | logging.Logger, 
        term_id: Optional[str] = None, 
        term_id_color = BCOLORS.OKGRAY, 
        term_log_level = "INFO",
        file_path: Optional[str] = None,
        file_log_level: _FileLogLevelT = "_ALL",
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

    def __formatTermID(term_id: str) -> str:
        fix_len = 8
        if len(term_id) > fix_len:
            return term_id[:fix_len-3] + "..."
        else:
            return term_id.rjust(fix_len)
    # set up terminal handler
    _ch = logging.StreamHandler()
    _ch.setLevel(term_log_level)
    _ch.setFormatter(logging.Formatter(term_id_color +f'[{__formatTermID(term_id)}]'
                                       +BCOLORS.OKCYAN + ' %(asctime)s '
                                       +BCOLORS.OKCYAN + '[%(levelname)s] ' + BCOLORS.ENDC + ' %(message)s'))
    logger.addHandler(_ch)

    __file_fommatter = logging.Formatter('%(asctime)s [%(levelname)s] - %(message)s')
    if file_log_level != "_ALL":
        # get less critical log level and set it to be the level of logger
        logger.setLevel(min(logging.getLevelName(term_log_level), logging.getLevelName(file_log_level)))

        # set up file handler
        if file_path is not None:
            _fh = logging.FileHandler(file_path)
            _fh = RotatingFileHandler(file_path, "a", maxBytes = 1024*1024, backupCount = 1, encoding = "utf-8")
            _fh.setLevel(file_log_level)
            _fh.setFormatter(__file_fommatter)
            logger.addHandler(_fh)
    else:
        # set up a file handler for each level!
        class LevelFilter(logging.Filter):
            def __init__(self, level):
                self.level = level
            def filter(self, record):
                return record.levelno == self.level

        logger.setLevel(logging.DEBUG)
        if file_path is not None:
            # set up file handlers
            for _level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
                _fh = logging.FileHandler(file_path + "." + _level.lower())
                _fh = RotatingFileHandler(file_path + "." + _level.lower(), "a", maxBytes = 1024*1024, backupCount = 1, encoding = "utf-8")
                _fh.setLevel(_level)
                _fh.addFilter(LevelFilter(logging.getLevelName(_level)))
                _fh.setFormatter(__file_fommatter)
                logger.addHandler(_fh)
            # set up a file handler for all levels
            _fh = logging.FileHandler(file_path)
            _fh = RotatingFileHandler(file_path, "a", maxBytes = 1024*1024, backupCount = 1, encoding = "utf-8")
            _fh.setLevel(logging.DEBUG)
            _fh.setFormatter(__file_fommatter)
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


## ----- Custom logger -----
class Logger():
    # https://cloud.tencent.com/developer/article/1643418
    def __init__(self, file_obj: TextIOWrapper, write_to_terminal = True):
        self.terminal = sys.stdout
        self.log = file_obj
        self.write_terminal = write_to_terminal
 
    def write(self, message):
        if self.write_terminal:
            self.terminal.write(message)
        self.log.write(message)
 
    def flush(self):
        if self.write_terminal:
            self.terminal.flush()

def logFunc(log_path = LOG_FILE):
    def wapper(func):
        @wraps(func)
        def _func(*args, **kwargs):
            std_out = sys.stdout
            std_err = sys.stderr
            with open(log_path, "a") as log_file:
                sys.stdout = Logger(log_file)
                sys.stderr = Logger(log_file)
                print("{time}: {name}".format(time = TimeUtils.localNowStr(), name = func.__name__))
                func(*args, **kwargs)
            sys.stdout = std_out
            sys.stderr = std_err
        return _func
    return wapper
    