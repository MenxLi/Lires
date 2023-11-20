

import os
from pprint import pprint
from lires.initLogger import initDefaultLogger; initDefaultLogger()
from lires.confReader import DATABASE_DIR
from lires.core.fileTools import addDocument, DBConnection, FileManipulator
from lires.core.dataClass import DataPoint, DataBase

import logging
logger = logging.getLogger("lires")
logger.info("Hi")

test_bibtex = """
@inproceedings{wynn2023diffusionerf,
  title={DiffusioNeRF: Regularizing Neural Radiance Fields with Denoising Diffusion Models},
  author={Wynn, Jamie and Turmukhambetov, Daniyar},
  booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition},
  pages={4180--4189},
  year={2023}
}
"""

pdf_path = "/Users/monsoon/Downloads/Wynn_DiffusioNeRF_Regularizing_Neural_Radiance_Fields_With_Denoising_Diffusion_Models_CVPR_2023_paper.pdf"




def testFileManipulator(fm: FileManipulator):
    conn = fm.conn
    uid = addDocument(conn, test_bibtex, doc_src=pdf_path); assert uid

    assert fm.hasFile()
    assert fm.file_p
    assert fm.file_extension == ".pdf"

    fm.deleteDocument()
    assert fm.hasFile() is False
    assert fm.file_p is None
    assert fm.file_extension == ""

    fm.addFile(pdf_path)
    assert fm.hasFile()
    assert fm.file_p
    assert fm.file_extension == ".pdf"

    print("Doc size: ", fm.getDocSize())
    fm.writeTags(["A", "AB", "AB->C"])
    print(fm.getTags())
    fm.setWebUrl("https://bing.com")
    print(fm.getWebUrl())
    fm.deleteDocument()
    # fm.openFile()

db_pth = DATABASE_DIR
conn = DBConnection(db_pth)
uid = addDocument(conn, test_bibtex, doc_src=pdf_path); assert uid
# fm = FileManipulator(uid, conn)
fm = FileManipulator(uid, conn)
dp = DataPoint(fm)
# assert conn is fm.conn

assert fm.conn.db_dir == db_pth, (fm.conn.db_dir, db_pth)

testFileManipulator(fm)

pprint(dp.summary)

db = DataBase().init(db_pth)
print(db)