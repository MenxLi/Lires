import os
import re
import platform
import subprocess

def openFile(filepath):
    # https://stackoverflow.com/questions/434597/open-document-with-default-os-application-in-python-both-in-windows-and-mac-os

    if platform.system() == 'Darwin':       # macOS
        subprocess.Popen(('open', filepath))    # type: ignore
    elif platform.system() == 'Windows':    # Windows
        os.startfile(filepath)  # type: ignore
    else:                                   # linux variants
        subprocess.Popen(('xdg-open', filepath))

def isWebURL(text: str):
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, text) is None
