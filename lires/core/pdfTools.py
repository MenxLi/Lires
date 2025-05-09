import fitz     # PyMuPDF
from typing import Optional
import os, random, shutil
import aiohttp, os, zipfile, asyncio
import aiofiles
from tqdm import tqdm
from ..utils import UseTermColor
from ..config import TMP_DIR

# DEFAULT_PDFJS_DOWNLOADING_URL = "https://registry.npmjs.org/pdfjs-dist/-/pdfjs-dist-4.0.379.tgz"
# DEFAULT_PDFJS_DOWNLOADING_URL = "https://github.com/mozilla/pdf.js/releases/download/v4.2.67/pdfjs-4.2.67-legacy-dist.zip"
DEFAULT_PDFJS_DOWNLOADING_URL = "https://github.com/mozilla/pdf.js/releases/download/v4.10.38/pdfjs-4.10.38-dist.zip"
__pdfviewer_code_snippet = """
<script>
    // A snippet to modify the default viewer options
    // Added via automation with Lires.

    /*
    * @param { 'light' | 'dark' } name - The name of the color mode.
    * @returns { string } The CSS class name.
    */
    function getColorModeClass(name){
    switch (name) {
        case 'light':
        return 'is-light';
        case 'dark':
        return 'is-dark';
        default:
        return ' ';
    }
    }
    const urlParams = (new URL(document.location)).searchParams;
    let themeChangeFn = function() {};
    if (urlParams.has('color-mode')) {
    const colorMode = urlParams.get('color-mode');
    if (colorMode && (colorMode === 'dark' || colorMode === 'light')) {
        console.log('Setting color mode to ' + colorMode)
        themeChangeFn = function() {
        // check if other color mode is already set
        const otherColorMode = colorMode === 'dark' ? 'light' : 'dark';
        const otherColorModeClass = getColorModeClass(otherColorMode);
        if (document.documentElement.classList.contains(otherColorModeClass)) {
            document.documentElement.classList.remove(otherColorModeClass);
        }
        // add color mode class
        document.documentElement.classList.add(getColorModeClass(colorMode));
        }
    }
    }

    window.onload = function() {
        themeChangeFn();
        document.querySelector("#viewerContainer").classList.add("scrollable");
    }
</script>
<style>
    :root.is-light, :root {
    --color-background-soft: #f7f7f7;
    --color-border: rgba(0, 0, 0, 0.12);
    }
    :root.is-dark {
    --color-background-soft: #303030;
    --color-border: rgba(90, 90, 90, 0.48);
    }
    html{
    --scrollbarBG: var(--color-background-soft);
    --thumbBG: var(--color-border);
    }
    body::-webkit-scrollbar, 
    .panel::-webkit-scrollbar, 
    .scrollable::-webkit-scrollbar,
    .hover-scrollable::-webkit-scrollbar{
    width: 15px;
    }
    body::-webkit-scrollbar-track, 
    .panel::-webkit-scrollbar-track, 
    .scrollable::-webkit-scrollbar-track, 
    .hover-scrollable::-webkit-scrollbar-track {
    background: var(--scrollbarBG);
    }
    body::-webkit-scrollbar-thumb, 
    .panel::-webkit-scrollbar-thumb, 
    .scrollable::-webkit-scrollbar-thumb,
    .hover-scrollable::-webkit-scrollbar-thumb {
    background-color: var(--thumbBG) ;
    border-radius: 7px;
    border: 3px solid var(--scrollbarBG);
    }
</style>
"""

async def download_default_pdfjs_viewer(
        dst_dir: str,
        download_url: str = DEFAULT_PDFJS_DOWNLOADING_URL, 
        force: bool = False) -> bool:
    print("Will download pdfjs and place it to: {}".format(dst_dir))
    if not force and os.path.exists(dst_dir):
        with UseTermColor("red"):
            print("Should delete old pdf.js viewer first: ", dst_dir)
            print("call: rm -rf {}".format(dst_dir))
        return False
    tmp_download = os.path.join(TMP_DIR, download_url.split("/")[-1])

    print("Downloading pdf.js from {}".format(download_url))

    # use aiohttp instead
    SUCCESS = True
    def ensureRes(response: aiohttp.ClientResponse):
        if response.status != 200 and response.status != 302:
            raise RuntimeError("({})".format(response.status))
        return True
    try:
        async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=False),
                timeout=aiohttp.ClientTimeout(total=60),
                trust_env=True      # for proxy
            ) as session:
            async with session.head(download_url) as response:
                ensureRes(response)
                total_size_in_bytes = int(response.headers["Content-Length"])
            progress_bar = tqdm(total=total_size_in_bytes, unit='B', unit_scale=True, desc="Downloading PDF.js")
            async with session.get(download_url) as response:
                ensureRes(response)
                with open(tmp_download, "wb") as f:
                    async for data in response.content.iter_chunked(1024):
                        f.write(data)
                        progress_bar.update(len(data))
            if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
                print("ERROR, something went wrong")
                SUCCESS = False
    except RuntimeError as e:
        with UseTermColor("red"):
            print("ERROR: {}".format(e))
        SUCCESS = False

    if not SUCCESS:
        if os.path.exists(tmp_download):
            os.remove(tmp_download)
        return False
    
    print("Extracting to default viewer location...")
    if force and os.path.exists(dst_dir):
        shutil.rmtree(dst_dir)
    os.mkdir(dst_dir)
    assert tmp_download.endswith(".zip")
    with zipfile.ZipFile(tmp_download, "r", compression=zipfile.ZIP_DEFLATED) as zp:
        zp.extractall(path = dst_dir)

    print("Downloaded PDF.js to: {}".format(dst_dir))
    os.remove(tmp_download)
    viewer_index_file = os.path.join(dst_dir, "web", "viewer.html")
    # add a snippet to modify the default viewer options
    print("Inject code snippet.")
    with open(viewer_index_file, "r", encoding='utf-8') as f:
        viewer_index = f.read()
        viewer_index = viewer_index.replace("</body>", __pdfviewer_code_snippet + "\n</body>")
    with open(viewer_index_file, "w", encoding='utf-8') as f:
        f.write(viewer_index)
    print("Done.")
    return True

async def init_pdf_viewer(dst_dir: str):
    if os.path.exists(dst_dir) \
        and not os.listdir(dst_dir)==[] \
        and os.path.exists(os.path.join(dst_dir, "web", "viewer.html")):
        return None

    lock_file = os.path.join(os.path.dirname(dst_dir), "pdfjs_downloading.lock")
    this_pid = os.getpid()
    while os.path.exists(lock_file):
        print(f"[{this_pid}] Waiting for other process to download pdfjs..."
                f"lock file: {lock_file}")
        await asyncio.sleep(3)

    await asyncio.sleep(random.random()*0.01)   # to avoid resouce conflict
    with open(lock_file, "w", encoding="utf-8") as f:
        f.write(str(this_pid))
    try:
        await download_default_pdfjs_viewer(force=True, dst_dir=dst_dir)
    except Exception as e:
        with UseTermColor("red"):
            print("ERROR: {}".format(e))
        print("Failed to download pdfjs, exit.")
        exit(1)
    finally:
        os.remove(lock_file)

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

    async def __aenter__(self):
        async with aiofiles.open(self.fpath, "rb") as f:
            self.doc = fitz.open(stream = await f.read(), filetype="pdf") # type: ignore
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        self.doc.close()

    def get_text(self, no_new_line = True, smaller_space = True) -> str:
        text = chr(12).join([page.get_text() for page in self.doc]) # type: ignore
        if no_new_line:
            text = text.replace("\n", " ")
        if smaller_space:
            # replace multiple spaces with one space
            text = " ".join(text.split())
        return text
    
    def remove_images(self) -> None:
        """ 
        Remove all images in the pdf.
        """
        for i in range(self.doc.page_count):
            for img in self.doc.get_page_images(i):
                xref = img[0]
                self.doc._deleteObject(xref)
    
    def to_bytes(self) -> bytes:
        return self.doc.write()

async def get_pdf_text(pdf_path: str, max_word: Optional[int] = None, possible_offset: int = 0) -> str:
    """
    possible_offset: if the pdf has more words than max_word, 
        then the offset will be used to get the text from the start of the pdf. 
        then actual offset will be calculated based on the number of words in the pdf.
    """
    async with PDFAnalyser(pdf_path) as doc:
        pdf_text_ori = doc.get_text()

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