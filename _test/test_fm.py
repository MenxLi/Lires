

import os
from pprint import pprint
from resbibman.initLogger import initLogger; initLogger()
from resbibman.confReader import RBM_HOME, getDatabase
from resbibman.core.fileTools import addDocument, DBConnection, FileManipulator
from resbibman.core.fileToolsV import FileManipulatorVirtual
from resbibman.core.dataClass import DataPoint, DataBase

import logging
logger = logging.getLogger("rbm")
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
    fm.setWebUrl("http://limengxun.com")
    print(fm.getWebUrl())
    fm.deleteDocument()
    # fm.openFile()

db_pth = getDatabase(True)
conn = DBConnection(db_pth)
uid = addDocument(conn, test_bibtex, doc_src=pdf_path); assert uid
# fm = FileManipulator(uid)
fmv = FileManipulatorVirtual(uid)
fmv._forceOffline()
# assert conn is fm.conn

testFileManipulator(fmv)
# testFileManipulator(fmv)

dp = DataPoint(fmv)
pprint(dp.summary)

db = DataBase().init(db_pth, force_offline=True)
print(db)