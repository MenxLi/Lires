"""
There are currently two ways to use the API to add data to the database:
    1. Top Down: create a database object and use the object to add data
    2. Bottom Up: create a sqlite connection and use the connection to add data
This script shows how to use the Bottom Up approach to add data to the database.
We recommend using the Top Down approach because it's more convenient and more flexible.
However, the Bottom Up approach is useful when you want to use the API without creating a database object.

In the Bottom Up approach, we create a sqlite connection and use the connection to add data to the sqlite database, 
    then, we create a FileManipulatorVirtual object which is in charge of IO operations of the data,
    afterward, we create a DataPoint object which is the core data structure of lires out of the FileManipulatorVirtual object.
"""

import os
from pprint import pprint
from lires.api import addDocument, FileManipulatorVirtual, DBConnection, DataPoint

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

# ================== Bottom Up ==================
# * No database object is created, all operations are done through DataPoint and FileManipulatorVirtual *

# create a sqlite connection
db_conn = DBConnection(db_dir)

# add document to sqlite database and obtain the data id
uid = addDocument(
    db_conn = db_conn,
    citation=bibtex,
    doc_src = doc_path,
)
assert uid is not None  # check if the document is added successfully

# create a FileManipulator object, all IO operations are done through this object
fm = FileManipulatorVirtual(uid, db_local = db_conn)

# create a DataPoint object, which is the core data structure of lires
data = DataPoint(fm)
data._forceOffline()    # force the program to use offline mode, otherwise the program will try to connect to the server specified in the config file
# ===============================================

# write some notes
fm.writeComments("This is a note")

# add file url
fm.setWebUrl("https://arxiv.org/abs/1706.03762")

# maybe add pdf file later if it's not added by addDocument
# fm.addFile("your_pdf_path")      # equivalent to data.addFile("your_pdf_path")

pprint(data.summary)
