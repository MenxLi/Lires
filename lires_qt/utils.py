import fitz     # PyMuPDF
from lires.core.pdfTools import PDFAnalyser
import logging, os
from .config import ICON_PATH
from PyQt6 import QtGui


def getPDFCoverAsQPixelmap(f_path: str):
    def _getCoverIcon(doc: fitz.Document):
        page = doc.load_page(0)
        cover = __renderPDFpage(page)
        return cover

    cover: QtGui.QPixmap
    try:
        with PDFAnalyser(f_path) as doc:
            cover = _getCoverIcon(doc)
        return cover
    except Exception as E:
        logging.getLogger("lires").debug(f"Error happened while rendering pdf cover: {E}")
        cover= QtGui.QPixmap()
        cover.convertFromImage(QtGui.QImage(os.path.join(ICON_PATH, "error-48px.png")))
    return cover

def __renderPDFpage(page_data, for_cover=False):
    zoom_matrix = fitz.Matrix(4, 4)
    if for_cover:
        zoom_matrix = fitz.Matrix(1, 1)
    
    pagePixmap = page_data.get_pixmap(
        matrix = zoom_matrix, 
        alpha=False) 
    imageFormat = QtGui.QImage.Format.Format_RGB888 
    pageQImage = QtGui.QImage(
        pagePixmap.samples,
        pagePixmap.width, 
        pagePixmap.height, 
        pagePixmap.stride,
        imageFormat)

    pixmap = QtGui.QPixmap()
    pixmap.convertFromImage(pageQImage)
    return pixmap