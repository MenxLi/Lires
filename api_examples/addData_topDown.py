"""
There are currently two ways to use the API to add data to the database:
    1. Top Down: create a database object and use the object to add data
    2. Bottom Up: create a sqlite connection and use the connection to add data
This script shows how to use the Top Down approach to add data to the database.
We recommend using the Top Down approach because it's more convenient and more flexible.

In the Top Down approach, we create a database object and use the object to obtain a sqlite connection,
    then we use the sqlite connection to add data to the sqlite database (physical database), 
    afterward we use the database object to load the data from the sqlite database and obtain a DataPoint object.
"""

import os
from pprint import pprint
from lires.api import addDocument, DataBase

this_dir = os.path.dirname(os.path.abspath(__file__))

db_dir = os.path.join(this_dir, ".TempDir", "Database")
if not os.path.exists(db_dir): os.makedirs(db_dir)
## [Optional] Get database path from config file
# from lires.confReader import getConf
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
database = DataBase(db_dir)     # equivalent to DataBase().init(db_dir)

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
# the data is a datapoint object, which is the core data structure of lires
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
