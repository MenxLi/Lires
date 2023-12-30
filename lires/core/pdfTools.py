import fitz     # PyMuPDF
from typing import Optional
import os
import requests, os, zipfile
from tqdm import tqdm
from .utils import UseTermColor
from ..confReader import PDF_VIEWER_DIR, TMP_DIR

DEFAULT_PDFJS_DOWNLOADING_URL = "https://github.com/mozilla/pdf.js/releases/download/v4.0.269/pdfjs-4.0.269-dist.zip"

def downloadDefaultPDFjsViewer(download_url: str = DEFAULT_PDFJS_DOWNLOADING_URL, force: bool = False) -> bool:
    print("Will download pdfjs and place it to: {}".format(PDF_VIEWER_DIR))
    if not force and os.path.exists(PDF_VIEWER_DIR):
        with UseTermColor("red"):
            print("Should delete old pdf.js viewer first: ", PDF_VIEWER_DIR)
            print("call: rm -rf {}".format(PDF_VIEWER_DIR))
        return False
    tmp_download = os.path.join(TMP_DIR, "pdfjs.zip")
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

    SUCCESS = True
    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        print("ERROR, something went wrong")
        SUCCESS = False
    if response.status_code != 200:
        print("ERROR ({})".format(response.status_code))
        SUCCESS = False

    if not SUCCESS:
        if os.path.exists(tmp_download):
            os.remove(tmp_download)
        return False
    
    print("Extracting to default viewer location...")
    os.mkdir(PDF_VIEWER_DIR)
    with zipfile.ZipFile(tmp_download, "r", compression=zipfile.ZIP_DEFLATED) as zp:
        zp.extractall(path = PDF_VIEWER_DIR)
    print("Finished. downloaded PDF.js to: {}".format(PDF_VIEWER_DIR))
    os.remove(tmp_download)
    return True

if not os.path.exists(PDF_VIEWER_DIR) \
    or os.listdir(PDF_VIEWER_DIR)==[] \
    or not os.path.exists(os.path.join(PDF_VIEWER_DIR, "web", "viewer.html")):
    downloadDefaultPDFjsViewer(force=True)

# https://pymupdf.readthedocs.io/en/latest/index.html
class PDFAnalyser:
    def __init__(self, fpath: str) -> None:
        self.fpath = fpath
        self.doc: fitz.Document
    
    def __enter__(self):
        self.doc = fitz.open(self.fpath) # type: ignore
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.doc.close()

    def getText(self, no_new_line = True, smaller_space = True) -> str:
        text = chr(12).join([page.get_text() for page in self.doc]) # type: ignore
        if no_new_line:
            text = text.replace("\n", " ")
        if smaller_space:
            # replace multiple spaces with one space
            text = " ".join(text.split())
        return text

def getPDFText(pdf_path: str, max_word: Optional[int] = None, possible_offset: int = 0) -> str:
    """
    possible_offset: if the pdf has more words than max_word, 
        then the offset will be used to get the text from the start of the pdf. 
        then actual offset will be calculated based on the number of words in the pdf.
    """
    with PDFAnalyser(pdf_path) as doc:
        pdf_text_ori = doc.getText()

    n_words = len(pdf_text_ori.split())
    if n_words == 0:
        return ""
    if max_word is None:
        max_word = n_words
    
    # need more testing...
    if n_words > max_word + possible_offset:
        offset = possible_offset
    elif n_words > max_word:
        offset = n_words - max_word
    else:
        offset = 0
    
    if offset + max_word > n_words:
        max_word = n_words - offset
    
    pdf_text = " ".join(pdf_text_ori.split()[offset:offset + max_word])
    return pdf_text