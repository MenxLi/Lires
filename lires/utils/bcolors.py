
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