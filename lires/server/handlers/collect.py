
from ._base import *
from lires.cmd.collect import LiresRetriver
import json

class CollectHandler(tornado.web.RequestHandler, RequestHandlerMixin):
    """Command with arguments"""
    @keyRequired
    def post(self):
        if not self.user_info["is_admin"]:
            # only admin access
            raise tornado.web.HTTPError(403)

        self.allowCORS()
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
            d_summary = self.db[actual_uuid].summary
            self.broadcastEventMessage({
                'type': 'add_entry',
                'uuid': d_summary['uuid'],
                'datapoint_summary': d_summary,
            })
            return self.write(json.dumps(d_summary))
        else:
            # most likely the file is already in the database
            raise tornado.web.HTTPError(409)    