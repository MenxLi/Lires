

from pprint import pprint
from lires.utils import initDefaultLogger; initDefaultLogger()
from lires.confReader import DATABASE_DIR
from lires.core.fileTools import addDocument, FileManipulator
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

pdf_path = "/Users/monsoon/Downloads/2312.13469_compressed.pdf"

def testFileManipulator(fm: FileManipulator):
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

if __name__ == "__main__":
  db_pth = DATABASE_DIR
  db = DataBase().init(db_pth)

  conn = db.conn
  uid = addDocument(conn, test_bibtex, doc_src=pdf_path); assert uid
  fm = FileManipulator(uid, conn)
  dp = DataPoint(fm)

  assert fm.conn.db_dir == db_pth, (fm.conn.db_dir, db_pth)

  testFileManipulator(fm)

  pprint(dp.summary)

  print(db)