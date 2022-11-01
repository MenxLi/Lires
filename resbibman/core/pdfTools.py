try:
    import fitz
except:
    pass
import os
from PyQt6 import QtGui
import logging

import requests, os, zipfile
from tqdm import tqdm
from ..confReader import ICON_PATH, DEFAULT_PDF_VIEWER_DIR, TMP_DIR

def render_pdf_page(page_data, for_cover=False):
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

def getPDFCoverAsQPixelmap(f_path: str):
    try:
        doc = fitz.open(f_path)
        page = doc.load_page(0)
        cover = render_pdf_page(page, True)
    except Exception as E:
        logging.getLogger("rbm").debug(f"Error happened while rendering pdf cover: {E}")
        cover= QtGui.QPixmap()
        cover.convertFromImage(QtGui.QImage(os.path.join(ICON_PATH, "error-48px.png")))
    return cover

def downloadDefaultPDFjsViewer() -> bool:
    tmp_download = os.path.join(TMP_DIR, "pdfjs.zip")
    download_url = "https://github.com/mozilla/pdf.js/releases/download/v3.0.279/pdfjs-3.0.279-dist.zip"
    print("Downloading pdf.js from {}".format(download_url))
    # https://stackoverflow.com/a/37573701/6775765
    response = requests.get(download_url, stream=True)
    total_size_in_bytes= int(response.headers.get('content-length', 0))
    block_size = 1024 #1 Kibibyte
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
    with open(tmp_download, 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()
    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        print("ERROR, something went wrong")
        return False
    
    print("Extracting to default viewer location...")
    with zipfile.ZipFile(tmp_download, "r", compression=zipfile.ZIP_DEFLATED) as zp:
        zp.extractall(path = DEFAULT_PDF_VIEWER_DIR)
    print("Finished. downloaded PDF.js to: {}".format(DEFAULT_PDF_VIEWER_DIR))
    os.remove(tmp_download)