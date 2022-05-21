import zipfile, os, tempfile, shutil, logging
from .utils import openFile, randomAlphaNumeric
from . import globalVar as G

def openTmp_hpack(hpack_path: str) -> bool:
    """
    Unpack a html file to a temporary directory
    """
    tmp_dir = tempfile.gettempdir()
    tmp_dir = unpackHtml(hpack_path, os.path.join(tmp_dir, randomAlphaNumeric(10)))
    G.tmpdirs.append(tmp_dir)
    G.logger_rbm.debug("Created temporary directory for HTML files: {}".format(tmp_dir))

    h_file = None
    if "index.html" in os.listdir(tmp_dir):
        h_file = "index.html"
    else:
        for f_ in os.listdir(tmp_dir):
            if f_.endswith(".html"):
                h_file = f_

    if h_file is None:
        return False

    openFile(os.path.join(tmp_dir, h_file))
    return True

def packHtml(html_file: str, dst: str, del_src: bool = False) -> str:
    """
    Generate .hpack file
    return generated hpack path
    """
    if dst.endswith('.hpack'):
        pass
    elif os.path.exists(dst) and os.path.isdir(dst):
        dst_path = os.path.join(dst, "html_pack.hpack")
    else: 
        raise ValueError("Invalid destination.")

    assets_dir = findHtmlAssetDir(html_file)
    if not assets_dir:
        raise FileNotFoundError("No assets directory found for the html.")

    to_pack = [html_file]
    to_pack += getAllFilePaths(assets_dir)

    html_base_dir = os.path.dirname(html_file)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zp:
        for f_ in to_pack:
            zp.write(f_, arcname=f_.replace(html_base_dir, ""), compress_type=zipfile.ZIP_DEFLATED)

    if del_src:
        shutil.rmtree(assets_dir)
        os.remove(html_file)

    return dst

def unpackHtml(hpack_path: str, dst: str) -> str:
    if not os.path.exists(dst):
        os.mkdir(dst)
    elif os.path.exists(dst) and len(os.listdir(dst))==0:
        pass
    else:
        raise ValueError("Invalid destination, already exists (none empty).")

    with zipfile.ZipFile(hpack_path, "r", compression=zipfile.ZIP_DEFLATED) as zp:
        zp.extractall(path = dst)

    return dst


def findHtmlAssetDir(html_file: str) -> str:
    """
    Find assosiated assets directory with an html file
    Search in the html folder
    """
    assert html_file.endswith('.html')
    base_dir = os.path.dirname(html_file)
    file_name = os.path.basename(html_file)
    base_name = file_name[:-5]

    dir_name = os.path.join(base_dir, base_name+"_files")

    if os.path.exists(dir_name) and os.path.isdir(dir_name):
        return dir_name
    else:
        return ""

def getAllFilePaths(directory):
    file_paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)
    return file_paths