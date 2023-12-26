"""
Get documents: document file / web page / comments
"""
from ._base import *
import os, json
from lires.confReader import TMP_DIR, ACCEPTED_EXTENSIONS

class DocHandler(RequestHandlerBase):
    def get(self, uuid):
        file_p = self.db[uuid].fm.file_p
        if isinstance(file_p, str):
            if file_p.endswith(".pdf"):
                with open(file_p, "rb") as f:
                    self.set_header("Content-Type", 'application/pdf; charset="utf-8"')
                    self.set_header("Content-Disposition", "inline; filename={}.pdf".format(uuid))
                    # self.set_header("Access-Control-Allow-Origin", "*")
                    self.write(f.read())
                    return
        self.write("The file not exist or is not PDF file.")
    
    @keyRequired
    def put(self, uid):
        """
        Upload document file
        """
        # permission check
        dp = self.db[uid]
        if not self.user_info["is_admin"]:
            self.checkTagPermission(dp.tags, self.user_info["mandatory_tags"])

        file_info = self.request.files['file'][0]  # Get the file information
        file_data = file_info['body']  # Get the file data
        
        original_filename = file_info['filename']
        file_size = len(file_data)
        self.logger.info(f"Received file: {original_filename} ({file_size} bytes)")

        #check file extension
        ext = os.path.splitext(original_filename)[1]
        if ext not in ACCEPTED_EXTENSIONS:
            raise tornado.web.HTTPError(400, reason="File extension not allowed")
        
        # save the file to a temporary location
        tmp_file = os.path.join(TMP_DIR, "upload_" + uid + ext)
        with open(tmp_file, "wb") as f:
            f.write(file_data)
        
        # add the file to the document
        if not dp.fm.addFile(tmp_file):
            # remove the temporary file
            os.remove(tmp_file)
            # existing file
            raise tornado.web.HTTPError(409, reason="File already exists")

        dp.loadInfo()
        os.remove(tmp_file)
        
        d_summary = dp.summary
        self.logger.info(f"Document {uid} added")
        self.broadcastEventMessage({
            "type": 'update_entry',
            'uuid': uid,
            'datapoint_summary': d_summary
        })
        self.write(json.dumps(d_summary))
    
    @keyRequired
    def delete(self, uid):
        """
        Free a document from a file
        """
        dp = self.db[uid]
        if not self.user_info["is_admin"]:
            self.checkTagPermission(dp.tags, self.user_info["mandatory_tags"])

        if not dp.fm.deleteDocument():
            raise tornado.web.HTTPError(500, reason="Failed to delete file")
        self.logger.info(f"Document {uid} freed")
        dp.loadInfo()
        self.broadcastEventMessage({
            "type": 'update_entry',
            'uuid': uid,
            'datapoint_summary': dp.summary
        })
        self.write(json.dumps(dp.summary))