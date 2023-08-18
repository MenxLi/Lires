from lires.api.addArxiv import postAddArxiv
from hashlib import sha256

enc_key = sha256("123".encode("utf-8")).hexdigest()
print(postAddArxiv("arxiv:2101.00123", enc_key))
