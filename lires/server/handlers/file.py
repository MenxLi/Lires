from ._base import *
import os, shutil, json
from tornado import iostream
from lires.confReader import TMP_DIR, getConfV
from lires.core.compressTools import compressDir, decompressDir, compressSelected
from lires.core.dataClass import DataPoint
from lires.core.dbConn import DBFileInfo, DocInfo

class FileHandler(tornado.web.RequestHandler, RequestHandlerMixin):
    ZIP_TMP_DIR = os.path.join(TMP_DIR, "server_zips")
    
    def initialize(self):
        super().initialize()
        self.zip_tmp_dir = self.ZIP_TMP_DIR
        if not os.path.exists(self.zip_tmp_dir):
            os.mkdir(self.zip_tmp_dir)

    async def post(self):
        db = self.db

        self.setDefaultHeader()
        cmd = self.get_argument("cmd")
        uuid = self.get_argument("uuid")
        self.logger.info(f"Receiving file request: [{cmd}]({uuid})")

        permission =  self.checkKey()

        if cmd == "download-d_info":
            # download data info (DBFileInfo) only
            dp: DataPoint = db[uuid]
            if not permission["is_admin"]:
                # tag permission check
                self.checkTagPermission(dp.tags, permission["mandatory_tags"])
            info = dp.d_info; assert info is not None
            self.write(json.dumps(info))
            self.logger.debug(f"DBInfo {uuid} sent to client")

        elif cmd == "download":
            dp: DataPoint = db[uuid]
            if not permission["is_admin"]:
                # tag permission check
                self.checkTagPermission(dp.tags, permission["mandatory_tags"])
            tmp_zip = os.path.join(self.zip_tmp_dir, uuid+".zip")
            # gather selected files
            this_files = dp.fm.gatherFiles()
            compressed = compressSelected(this_files["root"], this_files["fname"], tmp_zip)
            with open(compressed, "rb") as f:
                # https://bhch.github.io/posts/2017/12/serving-large-files-with-tornado-safely-without-blocking/
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    try:
                        self.write(chunk) # write the chunk to response
                        await self.flush() # send the chunk to client
                    except iostream.StreamClosedError:
                        # this means the client has closed the connection
                        # so break the loop
                        break
                    finally:
                        # deleting the chunk is very important because 
                        # if many clients are downloading files at the 
                        # same time, the chunks in memory will keep 
                        # increasing and will eat up the RAM
                        del chunk
            self.logger.debug(f"File {uuid} sent to client")
        
        elif cmd == "upload":
            d_info: DBFileInfo = json.loads(self.get_argument("d_info"))
            if not permission["is_admin"]:
                # tag permission check
                tags = DocInfo.fromString(d_info["info_str"]).tags
                self.checkTagPermission(tags, permission["mandatory_tags"])
            # add through DBConnection
            self.db.conn.insertItem(d_info)
            assert uuid == d_info["uuid"], "uuid not match" # should not happen
            db_dir = db.conn.db_dir
            # remove possible existing old data
            if uuid in db:
                file_path = db[uuid].file_path
                if file_path is not None:
                    os.remove(file_path)
                misc_dir = db[uuid].fm.getMiscDir()
                if os.path.exists(misc_dir):
                    shutil.rmtree(misc_dir)
            # receive file to tmp dir
            tmp_zip = os.path.join(self.zip_tmp_dir, uuid+".zip")
            req_file = self.request.files
            f_body = req_file["file"][0]["body"]
            f_name = req_file["filename"][0]["body"].decode("utf-8")
            with open(tmp_zip, "wb") as fp:
                fp.write(f_body)
            # decompress to database directory
            decompressDir(tmp_zip, db_dir)
                
            # load data to database
            db.add(uuid)
            self.logger.debug(f"File {uuid} received from client")
        
        elif cmd == "delete":
            if not permission["is_admin"]:
                # tag permission check
                dp: DataPoint = db[uuid]
                self.checkTagPermission(dp.tags, permission["mandatory_tags"])
            if uuid in db:
                db.delete(uuid)
            else:
                print(f"{uuid} not in database, thus not deleted")
