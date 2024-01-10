from typing import Callable
import sys, os

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
