from typing import Callable, Optional
import tornado.web
import http.cookies
# from RBMWeb.backend.encryptServer import queryHashKey
from ..auth.encryptServer import queryAccount
from ..discussUtils import DiscussDatabase
from resbibman.core import globalVar as G
from resbibman.core.dataClass import DataBase
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

    def initdb(self):
        if G.hasGlobalAttr("server_db"):
            db: DataBase = G.getGlobalAttr("server_db")
            db.watchFileChange([])
        G.setGlobalAttr("server_db", loadDataBase(getLocalDatabasePath()))
        G.setGlobalAttr("server_discussion_db", DiscussDatabase())
    
    initdb(None)
    
    @property
    def db(self) -> DataBase:
        return G.getGlobalAttr("server_db")
    
    @property
    def discussion_db(self) -> DiscussDatabase:
        return G.getGlobalAttr("server_discussion_db")

    def checkCookieKey(self):
        """
        Authenticates key from cookies
        """
        #  cookies = self.cookies
        enc_key = self.get_cookie("RBM_ENC_KEY", "")
        return self._checkKey(enc_key)

    def checkKey(self):
        """
        Authenticates key from params
        """
        enc_key = self.get_argument("key")
        return self._checkKey(enc_key)

    def _checkKey(self, enc_key):
        if not enc_key:
            raise tornado.web.HTTPError(401) 

        if queryAccount(enc_key) is None:
            # unauthorized
            print("Reject key ({}), abort".format(enc_key))
            raise tornado.web.HTTPError(401) 
        self.enc_key = enc_key
        return True

    def setDefaultHeader(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Credentials", "true")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, PUT, DELETE, OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header("Access-Control-Expose-Headers", "*")