
from ._base import *
from lires.cmd.collect import LiresRetriver
import json

class CollectHandler(tornado.web.RequestHandler, RequestHandlerMixin):
    """Command with arguments"""
    def post(self):
        permission =  self.checkKey()

        if not permission["is_admin"]:
            # only admin access
            raise tornado.web.HTTPError(403)

        self.setDefaultHeader()
        retrive_str = self.get_argument("retrive")
        tags = json.loads(self.get_argument("tags", default="[]"))
        uuid = self.get_argument("uuid", default=None)
        download_doc = json.loads(self.get_argument("download_doc", default="false"))

        self.logger.info("Receiving collect command: {}, tags:{}".format(retrive_str, tags))

        assert isinstance(tags, list)
        assert isinstance(download_doc, bool)

        retriver = LiresRetriver(retrive_str)
        actual_uuid = retriver.run(
            database=self.db,
            download_doc = download_doc,
            uid = uuid,
            tags = tags,
            )
        if actual_uuid:
            return self.write(json.dumps(self.db[actual_uuid].summary))
        else:
            # most likely the file is already in the database
            raise tornado.web.HTTPError(409)    