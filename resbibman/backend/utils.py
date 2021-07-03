from io import TextIOWrapper
import time, datetime
import subprocess, os, platform, sys
from ..confReader import LOG_FILE
from functools import wraps

def getDateTime():
    return str(datetime.datetime.now())[:-7]

def openFile(filepath):
    # https://stackoverflow.com/questions/434597/open-document-with-default-os-application-in-python-both-in-windows-and-mac-os

    if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', filepath))
    elif platform.system() == 'Windows':    # Windows
        os.startfile(filepath)
    else:                                   # linux variants
        subprocess.call(('xdg-open', filepath))

class Logger():
    # https://cloud.tencent.com/developer/article/1643418
    def __init__(self, file_obj: TextIOWrapper):
        self.terminal = sys.stdout
        self.log = file_obj
 
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
 
    def flush(self):
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
                print("{time}: {name}".format(time = getDateTime(), name = func.__name__))
                func(*args, **kwargs)
            sys.stdout = std_out
            sys.stderr = std_err
        return _func
    return wapper
    

