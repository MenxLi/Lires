from ._base import *
import os, shutil
from resbibman.confReader import TMP_DIR, getConfV
from resbibman.core.compressTools import compressDir, decompressDir
from resbibman.core.dataClass import DataPoint

class FileHandler(tornado.web.RequestHandler, RequestHandlerBase):
    ZIP_TMP_DIR = os.path.join(TMP_DIR, "server_zips")
    
    def initialize(self):
        super().initialize()
        self.zip_tmp_dir = self.ZIP_TMP_DIR
        if not os.path.exists(self.zip_tmp_dir):
            os.mkdir(self.zip_tmp_dir)

    def post(self):
        db = self.db

        self.setDefaultHeader()
        cmd = self.get_argument("cmd")
        uuid = self.get_argument("uuid")
        print("Receiving file request: ", cmd, uuid)

        if not self.checkKey():
            return 

        if cmd == "download":
            dp: DataPoint = db[uuid]
            tmp_zip = os.path.join(self.zip_tmp_dir, uuid+".zip")
            compressed = compressDir(dp.data_path, tmp_zip)
            with open(compressed, "rb") as f:
                while True:
                    data = f.read(4096)
                    if not data:
                        break
                    self.write(data)
        
        elif cmd == "upload":
            tmp_zip = os.path.join(self.zip_tmp_dir, uuid+".zip")
            req_file = self.request.files
            f_body = req_file["file"][0]["body"]
            f_name = req_file["filename"][0]["body"].decode("utf-8")

            with open(tmp_zip, "wb") as fp:
                fp.write(f_body)

            dest = os.path.join(getConfV("database"), f_name)
            if os.path.exists(dest):
                shutil.rmtree(dest)
            dest = decompressDir(tmp_zip, dest)
            db.add(dest)
        
        elif cmd == "delete":
            if uuid in db:
                db.delete(uuid)
            else:
                print(f"{uuid} not in database, thus not deleted")
