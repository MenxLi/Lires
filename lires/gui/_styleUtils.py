import platform
from subprocess import Popen, PIPE
from PyQt6.QtGui import QPainter, QPixmap, QColor, QIcon
from ..confReader import getConfV


def isSysDarkMode() -> bool:
    """
    Detect if the system is in dark mode
    ref: https://stackoverflow.com/questions/65294987/detect-os-dark-mode-in-python
    """
    import darkdetect
    return darkdetect.isDark() # type: ignore

    def detect_darkmode_in_windows(): 
        try:
            import winreg
        except ImportError:
            return False
        registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        reg_keypath = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize'
        try:
            reg_key = winreg.OpenKey(registry, reg_keypath)
        except FileNotFoundError:
            return False

        for i in range(1024):
            try:
                value_name, value, _ = winreg.EnumValue(reg_key, i)
                if value_name == 'AppsUseLightTheme':
                    return value == 0
            except OSError:
                break
        return False

    if platform.system() == "Darwin":
        p = Popen("defaults read -g AppleInterfaceStyle", shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        if b"Dark" in stdout:
            return True
        else:
            return False

    if platform.system() == "Windows":
        return detect_darkmode_in_windows()

    return False

def isThemeDarkMode() -> bool:
    return "dark" in getConfV("stylesheet").lower()

DARKMODE = isThemeDarkMode()
COLOR_WHITE = "#cccccc"
COLOR_BLACK = "#333333"

def qIconFromSVG(svg_path: str, color = "black"):
    img = QPixmap(svg_path)
    qp = QPainter(img)
    qp.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    qp.fillRect( img.rect(), QColor(color) )
    qp.end()
    return QIcon(img)

def qIconFromSVG_autoBW(svg_path: str):
    """Auto black/white"""
    if DARKMODE:
        return qIconFromSVG(svg_path, COLOR_WHITE)
    else:
        return qIconFromSVG(svg_path, COLOR_BLACK)
