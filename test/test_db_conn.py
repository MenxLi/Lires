import os
from lires.confReader import RBM_HOME
from lires.core.dbConn import DBConnection, DBFileInfo

conn = DBConnection(os.path.join(RBM_HOME, "test.db"))

conn.insertItem({
    "uuid": "test",
    "doc_ext": ".pdf",
    "abstract":"",
    "bibtex": "",
    "comments": "",
    "info_str": "",
})
