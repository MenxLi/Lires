"""
Post commands to the server
"""
from ._base import *
import json

class CMDHandler(tornado.web.RequestHandler, RequestHandlerBase):
    def _reloadDB(self):
        self.setDefaultHeader()
        # self.db.watchFileChange([])
        # for k in self.db.keys():
        #     del self.db[k]
        # self.db.init(self.db_path)
        self.initdb()
        self.write("success")

    def get(self, cmd):
        if cmd == "reloadDB":
            print("receiving reload Database command")
            self._reloadDB()

class CMDArgHandler(tornado.web.RequestHandler, RequestHandlerBase):
    """Command with arguments"""
    def post(self):
        self.setDefaultHeader()
        cmd = self.get_argument("cmd")
        uuid = self.get_argument("uuid")
        args = json.loads(self.get_argument("args"))
        kwargs = json.loads(self.get_argument("kwargs"))
        print("Receiving argument command: ", cmd, uuid, args, kwargs)

        permission =  self.checkKey()
        if not permission["is_admin"]:
            # only admin access
            raise tornado.web.HTTPError(403)

        if cmd == "renameTagAll":
            self.db.renameTag(args[0], args[1])
        if cmd == "deleteTagAll":
            self.db.deleteTag(args[0])
        # if cmd == "rbm-collect":
        #     from resbibman.cmd.rbmCollect import exec as exec_rbmCollect
        #     d_path = exec_rbmCollect(args[0], **kwargs)
        #     if d_path:
        #         self.db.add(d_path)
        #     else:
        #         raise tornado.web.HTTPError(418) 