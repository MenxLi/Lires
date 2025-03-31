from __future__ import annotations
import zipfile, os
from typing import List

def get_all_file_paths(directory) -> List[str]:
    file_paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)
    return file_paths

def compress_dir(dir_path: str, dst_path: str) -> str:
    assert not (os.path.exists(dst_path) and os.path.isdir(dst_path)), \
        "dst exist and is a directory"
    files = get_all_file_paths(dir_path)
    with zipfile.ZipFile(dst_path, "w", zipfile.ZIP_DEFLATED) as zp:
        for f_ in files:
            zp.write(f_, arcname=f_.replace(dir_path, ""), compress_type=zipfile.ZIP_DEFLATED)
    return dst_path

def decompress_dir(zip_path: str, dst_path: str) -> str:
    assert os.path.isfile(zip_path)
    assert not (os.path.exists(dst_path) and os.path.isfile(dst_path)), \
        "dst exist and is a file"
    with zipfile.ZipFile(zip_path, "r", compression=zipfile.ZIP_DEFLATED) as zp:
        zp.extractall(path = dst_path)
    return dst_path

def compress_selected(root_dir: str, selected: List[str], dst_path: str) -> str:
    """
    root_dir: the root directory of the selected files
    selected: a list of file paths relative to root_dir
    dst_path: the path of the zip file to be generated
    """
    assert not (os.path.exists(dst_path) and os.path.isdir(dst_path)), \
        "dst exist and is a directory"
    all_files: list[str] = []
    for f_ in selected:
        fpath = os.path.join(root_dir, f_)
        assert os.path.exists(fpath), f"file {fpath} does not exist"
        if os.path.isdir(fpath):
            all_files.extend(get_all_file_paths(fpath))
        else:
            all_files.append(fpath)
    with zipfile.ZipFile(dst_path, "w", zipfile.ZIP_DEFLATED) as zp:
        for f_ in all_files:
            zp.write(f_, arcname=f_.replace(root_dir, ""), compress_type=zipfile.ZIP_DEFLATED)
    return dst_path