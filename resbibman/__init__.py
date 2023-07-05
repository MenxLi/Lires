import functools
import requests

# disable requests https cerificate verification globally
requests.get = functools.partial(requests.get, verify=False)
requests.post = functools.partial(requests.post, verify=False)