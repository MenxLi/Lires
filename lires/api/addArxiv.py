
from __future__ import annotations
import requests, json
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from lires.types.dataT import DataPointSummary

def postAddArxiv(
        arxiv_id: str, 
        enc_key: str,
        rbm_backend_url: str = "http://localhost:8080", 
        tags: list[str] = []) -> DataPointSummary | str:
    """
    A shortcut to post to rbm backend to add arxiv paper.
    - arxiv_id: arxiv id, e.g. "arxiv:2101.00123"
    - enc_key: sha256 encrypted rbm-key
    """
    arxiv_id = arxiv_id.strip().lower()
    if not arxiv_id.startswith("arxiv:"):
        # only number
        arxiv_id += "arxiv:"
    
    if not rbm_backend_url.endswith("/"):
        rbm_backend_url += "/"
    
    post_url = rbm_backend_url + "collect"
    post_args = {
        "retrive": arxiv_id,
        "tags": json.dumps(tags),
        "key": enc_key,
    }

    r = requests.post(post_url, data=post_args)
    if r.status_code == 200:
        return json.loads(r.text)
    else:
        return r.text