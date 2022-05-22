import zipfile, os
from typing import List

def getAllFilePaths(directory) -> List[str]:
    file_paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)
    return file_paths

def compressDir(dir_path: str, dst_path: str) -> str:
    assert not (os.path.exists(dst_path) and os.path.isdir(dst_path)), \
        "dst exist and is a directory"
    files = getAllFilePaths(dir_path)
    with zipfile.ZipFile(dst_path, "w", zipfile.ZIP_DEFLATED) as zp:
        for f_ in files:
            zp.write(f_, arcname=f_.replace(dir_path, ""), compress_type=zipfile.ZIP_DEFLATED)
    print("created zip file: ", dst_path)
    return dst_path

def decompressDir(zip_path: str, dst_path: str) -> str:
    assert os.path.isfile(zip_path)
    assert not (os.path.exists(dst_path) and os.path.isfile(dst_path)), \
        "dst exist and is a file"
    with zipfile.ZipFile(zip_path, "r", compression=zipfile.ZIP_DEFLATED) as zp:
        zp.extractall(path = dst_path)
    return dst_path