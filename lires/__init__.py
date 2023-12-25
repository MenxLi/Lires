import functools
import requests

from .core import globalVar as G
from .version import VERSION

G.init()
__version__ = VERSION

# disable requests https cerificate verification globally
requests.get = functools.partial(requests.get, verify=False)
requests.post = functools.partial(requests.post, verify=False)