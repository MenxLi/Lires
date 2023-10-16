from PyQt6.QtGui import QPainter, QPixmap, QColor, QIcon
from ..config import getGUIConf

def isThemeDarkMode() -> bool:
    return "dark" in getGUIConf()["stylesheet"].lower()

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
