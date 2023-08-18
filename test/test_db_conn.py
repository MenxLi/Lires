import os
from lires.confReader import LRS_HOME
from lires.core.dbConn import DBConnection, DBFileInfo

conn = DBConnection(os.path.join(LRS_HOME, "test.db"))

conn.insertItem({
    "uuid": "test",
    "doc_ext": ".pdf",
    "abstract":"",
    "bibtex": "",
    "comments": "",
    "info_str": "",
})
