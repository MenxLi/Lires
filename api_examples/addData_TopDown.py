

import os
from pprint import pprint
from resbibman.api import addDocument, DataBase

this_dir = os.path.dirname(os.path.abspath(__file__))

db_dir = os.path.join(this_dir, ".TempDir", "Database")
if not os.path.exists(db_dir): os.makedirs(db_dir)
## [Optional] Get database path from config file
# from resbibman.confReader import getConf
# db_dir = getConf()["database"]
print("Database path set to: ", db_dir)

# prepare document data
bibtex = """
@article{vaswani2017attention,
    author = "Vaswani, Ashish and Shazeer, Noam and Parmar, Niki and Uszkoreit, Jakob and Jones, Llion and Gomez, Aidan N and Kaiser, {\L}ukasz and Polosukhin, Illia",
    title = "Attention is all you need",
    journal = "Advances in neural information processing systems",
    volume = "30",
    year = "2017"
}
"""
doc_path = None         # pdf file path, set to None if no pdf file

# ================== Top Down ==================
# use force_offline=True to force the program to use offline mode
# otherwise the program will try to connect to the server specified in the config file
database = DataBase(db_dir, force_offline=True)     # equivalent to DataBase().init(db_dir, force_offline=True)

# get sqlite connection
db_conn = database.conn

# add document to sqlite database and obtain the data id
uid = addDocument(
    db_conn = db_conn,
    citation=bibtex,
    doc_src = doc_path,
)
assert uid is not None  # check if the document is added successfully

# ask database to load the data
# the data is a datapoint object, which is the core data structure of resbibman
data = database.add(uid)

# data = db[uid]
# pprint(data.summary)

# get the file manipulator object of the data, all IO operations are done through this object
fm = data.fm
# ===============================================

# write some notes
fm.writeComments("This is a note")

# add file url
fm.setWebUrl("https://arxiv.org/abs/1706.03762")

# maybe add pdf file later if it's not added by addDocument
# fm.addFile("your_pdf_path")      # equivalent to data.addFile("your_pdf_path")

pprint(data.summary)
