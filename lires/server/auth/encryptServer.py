
import os
from typing import Optional, List
from .account import Account, AccountPermission
from .._config import ACCOUNT_DIR

def _getAccountFilePath(hashkey):
    return os.path.join(ACCOUNT_DIR, hashkey + ".json")

def createAccount(hashkey: str, identifier: str, is_admin: bool, mandatory_tags) -> bool:
    aim_file = _getAccountFilePath(hashkey)
    if os.path.exists(aim_file):
        print("Account already exists")
        return False
    
    account = Account(hashkey = hashkey, identifier = identifier, is_admin = is_admin, mandatory_tags = mandatory_tags)
    account.toFile(aim_file)
    return True

def queryAccount(hashkey: str) -> Optional[AccountPermission]:
    """
    return None indicates that the account does not exist
    """
    aim_file = _getAccountFilePath(hashkey)
    if not os.path.exists(aim_file):
        return None
    account = Account().fromFile(aim_file)
    return account.permission

def deleteAccount(hashkey: str) -> bool:
    aim_file = _getAccountFilePath(hashkey)
    if not os.path.exists(aim_file):
        print("Account does not exist")
        return False
    else:
        os.remove(aim_file)
        return True

def getHashKeyByIdentifier(identifier: str) -> List[str]:
    ret = []
    for f in os.listdir(ACCOUNT_DIR):
        if not f.endswith(".json"):
            continue
        hashkey = f.strip(".json")
        aim_file = _getAccountFilePath(hashkey)
        account = Account().fromFile(aim_file)
        if account.identifier == identifier:
            ret.append(hashkey)
    return ret

def getAllAccounts():
    accounts = {}
    for f in os.listdir(ACCOUNT_DIR):
        if not f.endswith(".json"):
            continue
        hashkey = f.strip(".json")
        aim_file = _getAccountFilePath(hashkey)
        account = Account().fromFile(aim_file)
        accounts[hashkey] = account
    return accounts