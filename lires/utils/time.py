import datetime, logging, time, threading
from typing import Callable, TypeVar
from functools import wraps

CallVar = TypeVar("CallVar", bound = Callable)
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

def timedFunc(logger: logging.Logger) -> Callable[[CallVar], CallVar]:
    def _timedFunc(func: CallVar) -> CallVar:
        @wraps(func)
        def func_(*args, **kwargs):
            with Timer(func.__name__, print_func=lambda x: logger.debug(x)) as timer:
                return func(*args, **kwargs)
        return func_    # type: ignore
    return _timedFunc

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

def delay_exec(func: Callable, delay_time: float, *args, **kwargs):
    def _func():
        time.sleep(delay_time)
        func(*args, **kwargs)
    thread = threading.Thread(target=_func, args=())
    thread.start()
