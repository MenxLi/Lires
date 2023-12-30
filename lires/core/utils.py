from io import TextIOWrapper
import time, datetime, re, random, string, logging
import subprocess, os, platform, sys, threading
from typing import Callable, TypeVar
from ..confReader import LOG_FILE
from functools import wraps
from uuid import uuid4

CallVar = TypeVar("CallVar", bound = Callable)

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

def hintCall(func: CallVar) -> CallVar:
    logger = logging.getLogger("lires")
    @wraps(func)
    def func_(*args, **kwargs):
        logger.debug(f" [{func.__name__}] ")
        return func(*args, **kwargs)
    return func_    # type: ignore

def timedFunc(func: CallVar) -> CallVar:
    logger = logging.getLogger("lires")
    @wraps(func)
    def func_(*args, **kwargs):
        with Timer(func.__name__, print_func=lambda x: logger.debug(x)) as timer:
            return func(*args, **kwargs)
    return func_    # type: ignore

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

class ProgressBarCustom(object):
    def __init__(self, n_total, call: Callable[[str], None]):
        """
        - callback: Callable[[progress_str], None]
        """
        self._call = call
        self.n_toal = n_total
        self.current = 0

    @staticmethod
    def progressBarString(current: int, total: int):
        # To update later
        decimals = 1
        fill = '█'
        length = 20
        percent = ("{0:." + str(decimals) + "f}").format(100 * (current / float(total)))
        filledLength = int(length * current // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        #  return f"{current}/{total}"
        return f"{percent}% | {bar}"

    def next(self):
        self.current += 1
        to_show = self.progressBarString(self.current, self.n_toal)
        self._call(to_show)

class TimeUtils:
    LOCAL_TIMEZONE = datetime.datetime.now().astimezone().tzinfo
    @classmethod
    def nowStamp(cls):
        return cls.utcNow().timestamp()

    @staticmethod
    def toStr(dt: datetime.datetime) -> str:
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def stamp2Local(cls, stamp: float):
        local_datetime = datetime.datetime.fromtimestamp(stamp).replace(tzinfo=cls.LOCAL_TIMEZONE)
        return local_datetime

    @classmethod
    def stamp2Utc(cls, stamp: float):
        return cls.local2Utc(cls.stamp2Local(stamp))
    
    @staticmethod
    def utcNow() -> datetime.datetime:
        return datetime.datetime.now(datetime.timezone.utc)

    @classmethod
    def localNow(cls) -> datetime.datetime:
        return datetime.datetime.now(cls.LOCAL_TIMEZONE)

    @classmethod
    def utc2Local(cls, utc_datetime: datetime.datetime) -> datetime.datetime:
        # https://stackoverflow.com/a/39079819
        return utc_datetime.astimezone(cls.LOCAL_TIMEZONE)

    @classmethod
    def local2Utc(cls, local_datetime: datetime.datetime) -> datetime.datetime:
        return local_datetime.astimezone(datetime.timezone.utc)

    @classmethod
    def utcNowStr(cls) -> str:
        return datetime.datetime.strftime(cls.utcNow(), "%Y-%m-%d %H:%M:%S")

    @classmethod
    def localNowStr(cls) -> str:
        return datetime.datetime.strftime(cls.localNow(), "%Y-%m-%d %H:%M:%S")

    @classmethod
    def strUtcTimeToDatetime(cls, t: str) -> datetime.datetime:
        return datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S").replace(tzinfo = datetime.timezone.utc)

    @classmethod
    def strLocalTimeToDatetime(cls, t: str) -> datetime.datetime:
        return datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S").replace(tzinfo = cls.LOCAL_TIMEZONE)

def getDateTimeStr():
    return str(datetime.datetime.now())[:-7]

def strtimeToDatetime(t: str) -> datetime.datetime:
    return datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")

def openFile(filepath):
    # https://stackoverflow.com/questions/434597/open-document-with-default-os-application-in-python-both-in-windows-and-mac-os

    if platform.system() == 'Darwin':       # macOS
        subprocess.Popen(('open', filepath))    # type: ignore
    elif platform.system() == 'Windows':    # Windows
        os.startfile(filepath)  # type: ignore
    else:                                   # linux variants
        subprocess.Popen(('xdg-open', filepath))

def isWebURL(text: str):
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, text) is None

def delay_exec(func: Callable, delay_time: float, *args, **kwargs):
    def _func():
        time.sleep(delay_time)
        func(*args, **kwargs)
    thread = threading.Thread(target=_func, args=())
    thread.start()

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
    
def sUUID() -> str:
    """generate short UUID of length 21
    Returns:
        str: short string uuid
    """
    B16_TABLE = {
        "0": "0000",
        "1": "0001",
        "2": "0010",
        "3": "0011",
        "4": "0100",
        "5": "0101",
        "6": "0110",
        "7": "0111",
        "8": "1000",
        "9": "1001",
        "a": "1010",
        "b": "1011",
        "c": "1100",
        "d": "1101",
        "e": "1110",
        "f": "1111",
    }
    B64_LIST =[
        "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",\
        "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",\
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "+", "-"
    ]
    uuid_long = uuid4().hex
    # b_asciis = " ".join(["{0:08b}".format(ord(u), "b") for u in uuid_long])
    binary = "".join([B16_TABLE[u] for u in uuid_long])
    # len(binary) = 128
    uuid_short = ["0"]*21
    for i in range(0, len(binary)-2, 6):
        b = binary[i:i+6]
        integer = int(b, 2)
        uuid_short[i//6] = B64_LIST[integer]
    return "".join(uuid_short)

def ssUUID() -> str:
    """Short uuid of length 16

    Returns:
        str: uuid
    """
    suid = sUUID()
    return suid[:8] + suid[-8:]

def sssUUID() -> str:
    """Short uuid of length 8

    Returns:
        str: uuid
    """
    return ssUUID()[::2]

def randomAlphaNumeric(length: int):
    """Generate a random string"""
    str = string.ascii_lowercase
    return ''.join(random.choice(str) for i in range(length))

# https://stackoverflow.com/questions/287871/how-do-i-print-colored-text-to-the-terminal
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

    # Additional colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    LIGHTGRAY = '\033[37m'
    DARKGRAY = '\033[90m'
    LIGHTRED = '\033[91m'
    LIGHTGREEN = '\033[92m'
    LIGHTYELLOW = '\033[93m'
    LIGHTBLUE = '\033[94m'
    LIGHTMAGENTA = '\033[95m'
    LIGHTCYAN = '\033[96m'

class UseTermColor:
    def __init__(self, term_color: str):
        try:
            self._c = getattr(BCOLORS, term_color.upper())
        except KeyError:
            self._c = term_color
    
    def __enter__(self):
        print(self._c, end = "")
    
    def __exit__(self, exc_type, exc_value, traceback):
        print(BCOLORS.ENDC, end = "")