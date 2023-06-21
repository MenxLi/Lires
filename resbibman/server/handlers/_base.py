from __future__ import annotations
import logging
from typing import Callable, Optional, List
import tornado.web
import http.cookies
from ..auth.account import AccountPermission
from ..auth.encryptServer import queryAccount
from ..discussUtils import DiscussDatabase
from resbibman.core import globalVar as G
from resbibman.core.dataClass import DataBase, TagRule, DataTags
from resbibman.confReader import getConf

G.init()
def getLocalDatabasePath():
    return getConf()['database']

def loadDataBase(db_path: str):
    print("Loading database: {}".format(db_path))
    db = DataBase()
    db.init(db_path, force_offline=True)
    print("Finish.")
    return db


class RequestHandlerBase():
    get_argument: Callable
    get_cookie: Callable[[str, Optional[str]], Optional[str]]
    set_header: Callable
    cookies: http.cookies.SimpleCookie
    db_path: str = getLocalDatabasePath()
    logger = G.logger_rbm_server

    def initdb(self):
        if G.hasGlobalAttr("server_db"):
            db: DataBase = G.getGlobalAttr("server_db")
            db.watchFileChange([])
        G.setGlobalAttr("server_db", loadDataBase(getLocalDatabasePath()))
        G.setGlobalAttr("server_discussion_db", DiscussDatabase())
    
    initdb(None)    # type: ignore
    
    @property
    def db(self) -> DataBase:
        return G.getGlobalAttr("server_db")
    
    @property
    def discussion_db(self) -> DiscussDatabase:
        return G.getGlobalAttr("server_discussion_db")

    def checkCookieKey(self) -> AccountPermission:
        """
        Authenticates key from cookies
        """
        #  cookies = self.cookies
        enc_key = self.get_cookie("RBM_ENC_KEY", "")
        if not enc_key:
            enc_key = self.get_cookie("encKey", "")
        return self._checkKey(enc_key)

    def checkKey(self) -> AccountPermission:
        """
        Authenticates key from params, then cookies
        """
        try:
            enc_key = self.get_argument("key")
        except tornado.web.HTTPError:
            # no key defined in params, try cookies
            enc_key = self.get_cookie("RBM_ENC_KEY", "")
            if not enc_key:
                enc_key = self.get_cookie("encKey", "")
        return self._checkKey(enc_key)

    def _checkKey(self, enc_key) -> AccountPermission:
        self.logger.debug(f"check key: {enc_key}")
        if not enc_key:
            raise tornado.web.HTTPError(403) 

        res = queryAccount(enc_key)
        if res is None:
            # unauthorized
            print("Reject key ({}), abort".format(enc_key))
            raise tornado.web.HTTPError(403) 
        self.enc_key = enc_key
        return res
    
    @staticmethod
    def checkTagPermission(_tags: List[str] | DataTags, _mandatory_tags: List[str]):
        """
        Check if tags are dominated by mandatory_tags
        """
        tags = DataTags(_tags)
        mandatory_tags = DataTags(_mandatory_tags)
        RequestHandlerBase.logger.debug(f"check tags: {tags} vs {mandatory_tags}")
        if not mandatory_tags.issubset(tags.withParents()):
            raise tornado.web.HTTPError(402) 

    def setDefaultHeader(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Credentials", "true")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, PUT, DELETE, OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header("Access-Control-Expose-Headers", "*")