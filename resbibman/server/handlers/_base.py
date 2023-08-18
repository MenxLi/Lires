from __future__ import annotations
from typing import Callable, Optional, List
import tornado.web
import http.cookies
from ..auth.account import AccountPermission
from ..auth.encryptServer import queryAccount
from ..discussUtils import DiscussDatabase
from resbibman.core import globalVar as G
from resbibman.core.dataClass import DataBase, DataTags
from resbibman.confReader import getConf, VECTOR_DB_PATH
from tiny_vectordb import VectorDatabase

G.init()
def getLocalDatabasePath():
    return getConf()['database']

def loadDataBase(db_path: str):
    G.logger_rbm_server.info("Loading database: {}".format(db_path))
    db = DataBase()
    db.init(db_path, force_offline=True)
    return db


class RequestHandlerMixin():
    get_argument: Callable
    get_cookie: Callable[[str, Optional[str]], Optional[str]]
    set_header: Callable
    cookies: http.cookies.SimpleCookie
    db_path: str = getLocalDatabasePath()
    logger = G.logger_rbm_server

    def initdb(self):
        """
        Initialize / reload the database
        """
        self.logger.debug("Initializing server global database objects")
        if G.hasGlobalAttr("server_db"):
            db: DataBase = G.getGlobalAttr("server_db")
            db.destroy()
        G.setGlobalAttr("server_db", loadDataBase(getLocalDatabasePath()))
        G.setGlobalAttr("server_discussion_db", DiscussDatabase())
        if G.hasGlobalAttr("vec_db"):
            vec_db: VectorDatabase = G.getGlobalAttr("vec_db")
            vec_db.flush()
            vec_db.commit()
        G.setGlobalAttr(
            "vec_db", 
            VectorDatabase(VECTOR_DB_PATH, [
                {
                    "name": "doc_feature",
                    "dimension": 768
                },
            ]))
    
    # initdb(None)    # type: ignore
    
    @property
    def db(self) -> DataBase:
        if not G.hasGlobalAttr("server_db"):
            self.initdb()
        return G.getGlobalAttr("server_db")
    
    @property
    def vec_db(self) -> VectorDatabase:
        if not G.hasGlobalAttr("vec_db"):
            self.initdb()
        return G.getGlobalAttr("vec_db")
    
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
        RequestHandlerMixin.logger.debug(f"check tags: {tags} vs {mandatory_tags}")
        if not mandatory_tags.issubset(tags.withParents()):
            raise tornado.web.HTTPError(403) 

    def setDefaultHeader(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Credentials", "true")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, PUT, DELETE, OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header("Access-Control-Expose-Headers", "*")

__all__ = [
    "tornado",
    "RequestHandlerMixin",
    "G",
    ]