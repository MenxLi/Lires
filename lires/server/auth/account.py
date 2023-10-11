
"""
Each user's information will be saved in a json file,
the file will be named as the hashkey

RULES:

Previliges for administrator account:
    - rename/delete tag
    - being able to upload/delete/comment on all data
Non-admin account can't do that.

Mandatory tags are not applicable to admin accounts
Mandatory tags are (parent) tags that an account must have when:
    - upload data
    - delete data
    - comment (discuss) on data
"""

from typing import TypedDict, List, Optional
import json

class AccountPermission(TypedDict):
    is_admin: bool
    name: str
    enc_key: str
    mandatory_tags: List[str]

class Account:
    def __init__(self, **kwargs):
        # default constructor
        self.hashkey: Optional[str] = None
        self.name: str = ""
        self.is_admin: bool = False
        self.mandatory_tags: List[str] = []

        for k, v in kwargs.items():
            setattr(self, k, v)
    
    @property
    def permission(self) -> AccountPermission:
        return {
            "is_admin": self.is_admin,
            "name": self.name,
            "enc_key": self.hashkey if self.hashkey else "",
            "mandatory_tags": self.mandatory_tags
        }
        
    def fromFile(self, fpath: str):
        assert fpath.endswith(".json")
        with open(fpath, 'r') as fp:
            data = json.load(fp)
        for k, v in data.items():
            setattr(self, k, v)
        return self
    
    def toFile(self, fpath: str):
        assert fpath.endswith(".json")
        with open(fpath, "w") as fp:
            obj = dict()
            for k in ["hashkey", "name", "is_admin", "mandatory_tags"]:
                obj[k] = getattr(self, k)
            json.dump(obj, fp, indent=1)
        return self
    
    def detailString(self):
        lines = []
        for k in ["hashkey", "name", "is_admin", "mandatory_tags"]:
            lines.append(f" - {k}: {getattr(self, k)}")
        return "\n".join(lines)
    
    def __str__(self) -> str:
        ret = f"{self.hashkey} ({self.name})"
        if self.is_admin:
            ret = "* " + ret
        return ret

    __repr__ = __str__