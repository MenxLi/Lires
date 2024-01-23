from __future__ import annotations
import logging, sys, datetime
from logging.handlers import MemoryHandler
from typing import Optional, Literal
import threading
from .term import BCOLORS
import sqlite3

class DatabaseHandler(logging.Handler):
    """
    A logger that saves log to a database
    """
    _locks: dict[str, threading.Lock] = {}
    def __init__(self, name: str, db_path: str, db_level = "INFO"):
        super().__init__(level=logging.getLevelName(db_level))
        self.db_conn = sqlite3.connect(db_path, check_same_thread=False)
        self.db_table = name
        self.db_path = db_path
        self.db_level = db_level
        self.db_cursor = self.db_conn.cursor()
        with self.shared_lock:
            self.db_cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {self.db_table} "
                """
                (
                    date TEXT,
                    time TEXT, 
                    logger TEXT, 
                    level INTEGER, 
                    message TEXT
                )
                """
                )
            self.db_conn.commit()
    
    @property
    def shared_lock(self):
        return self.__class__._locks.setdefault(self.db_path, threading.Lock())
    
    def emit(self, record):
        with self.shared_lock:
            now_time = datetime.datetime.now()
            self.db_cursor.execute(
                f"INSERT INTO {self.db_table} VALUES (?, ?, ?, ?, ?)", 
                (
                    now_time.strftime('%Y-%m-%d'),
                    now_time.strftime('%I:%M:%S:%f %p'),
                    record.name,
                    record.levelno,
                    record.getMessage()
                ))
            self.db_conn.commit()
    
    def close(self):
        with self.shared_lock:
            self.db_conn.close()
    
    def __del__(self):
        self.close()

# ---- Main entry ----
TermLogLevelT = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
FileLogLevelT = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "_ALL"]
def setupLogger(
        _logger: str | logging.Logger, 
        term_id: Optional[str] = None, 
        term_id_color = BCOLORS.OKGRAY, 
        term_log_level: TermLogLevelT = "INFO",
        file_path: Optional[str] = None,
        file_log_level: FileLogLevelT = "_ALL",
        attach_execption_hook = False
        ) -> logging.Logger:
    """
    - term_id: will be used as terminal prefix
    - term_id_color: color of identifier
    - term_log_level: log level of terminal
    - file_path: file to save log, if specified, make sure it ends with .log, default to None (not save to file)
    - file_log_level: log level of save_file, if "_ALL", will save all levels
    - attach_execption_hook: whether to redirect unhandled exceptions to the logger
    """
    if file_path is not None:
        assert file_path.endswith(".log") or file_path.endswith(".db"), \
        "file_path must ends with .log or .db, got: {}".format(file_path)

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
    __mem_buffer_size = 1024    # 1 KB

    # set up a file handler for each level!
    class LevelFilter(logging.Filter):
        def __init__(self, level):
            self.level = level
        def filter(self, record):
            return record.levelno == self.level
    def _setupFileHandle(file_path: str, file_log_level: str, only_this_level = False):
        # set up file handler
        _fh = logging.FileHandler(file_path, "a", encoding = "utf-8")
        _fh.setLevel(file_log_level)
        _fh.setFormatter(__file_fommatter)
        if only_this_level:
            _fh.addFilter(LevelFilter(logging.getLevelName(file_log_level)))
        _mh = MemoryHandler(__mem_buffer_size, target=_fh, flushOnClose=True)
        logger.addHandler(_mh)
    def _setupDatabaseHandle(file_path: str, file_log_level: str, only_this_level = False):
        # set up file handler
        _dh = DatabaseHandler(
            logger.name,
            db_path=file_path, 
            db_level=file_log_level
            )
        _dh.setLevel(file_log_level)
        _dh.setFormatter(__file_fommatter)
        if only_this_level:
            _dh.addFilter(LevelFilter(logging.getLevelName(file_log_level)))
        logger.addHandler(_dh)

    # set up file handler
    if file_log_level != "_ALL":
        # get less critical log level and set it to be the level of logger
        logger.setLevel(min(logging.getLevelName(term_log_level), logging.getLevelName(file_log_level)))
        if file_path is not None and file_path.endswith(".log"):
            _setupFileHandle(file_path, file_log_level)
        if file_path is not None and file_path.endswith(".db"):
            _setupDatabaseHandle(file_path, file_log_level)
    else:
        logger.setLevel(logging.DEBUG)
        if file_path is not None and file_path.endswith(".log"):
            # set up file handlers
            for _level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
                # e.g. filename.debug.log
                __file_name = file_path[:-4] + "." + _level.lower() + file_path[-4:]
                _setupFileHandle(__file_name, _level, only_this_level=True)
            # set up a file handler for all levels
            _setupFileHandle(file_path, "DEBUG")
        if file_path is not None and file_path.endswith(".db"):
            _setupDatabaseHandle(file_path, "DEBUG")
    
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

