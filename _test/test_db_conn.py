import os
from resbibman.confReader import RBM_HOME
from resbibman.core.fileTools import DBConnection, DBFileInfo

conn = DBConnection(os.path.join(RBM_HOME, "test.db"))

conn.insertItem({
    "uuid": "test",
    "doc_ext": ".pdf",
    "abstract":"",
    "bibtex": "",
    "comments": "",
    "info_str": "",
})
