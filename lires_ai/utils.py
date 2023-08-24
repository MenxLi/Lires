
import torch
from typing import Callable, Optional
from logging.handlers import RotatingFileHandler
import sys, os, time, logging

def autoTorchDevice() -> str:
    if torch.cuda.is_available():
        return "cuda"
    # elif torch.has_mps:
    #     return "mps"
    else:
        return "cpu"


## BELOW ARE DUPICATED CODES FROM lires

class BCOLORS:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    OKGRAY = '\033[90m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Timer:
    def __init__(self, name: str = "", print_func: Callable[[str], None] = print):
        self.name = name
        self.start = time.time()
        self.end = None
        self.duration = None
        self.print_func = print_func

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time.time()
        self.duration = self.end - self.start
        if self.name:
            self.print_func(f"{self.name} finished in {self.duration:.3f} seconds")

class MuteEverything:
    def __init__(self, enable: bool = True):
        self.stdout = None
        self.stderr = None
        self.enable = enable
    def on(self):
        self.__enter__()
    def off(self):
        self.__exit__(None, None, None)

    def __enter__(self):
        if not self.enable:
            return
        # Redirect stdout and stderr to /dev/null
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.enable:
            return
        # Restore stdout and stderr
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = self.stdout
        sys.stderr = self.stderr

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