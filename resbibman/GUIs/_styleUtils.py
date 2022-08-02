import platform
from subprocess import Popen, PIPE
from PyQt6.QtGui import QPainter, QPixmap, QColor, QIcon


def isDarkMode() -> bool:
    """
    Detect if the system is in dark mode
    """
    if platform.system() == "Darwin":
        p = Popen("defaults read -g AppleInterfaceStyle", shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        if b"Dark" in stdout:
            return True

    return False

DARKMODE = isDarkMode()
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
