"""
The quary dialog for bibtex input
"""
import os, typing, difflib
from PyQt5.QtWidgets import QLabel, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFrame
from PyQt5.QtWidgets import QSizePolicy
from PyQt5 import QtCore

from ..core.dataClass import DataPoint, DataTags, DataBase
from .tagEditor import TagEditor
from ..core.bibReader import BibParser
from ..core.fileTools import FileGenerator, FileManipulator
from ..confReader import getConf, DOC_PATH
from ..core.utils import sssUUID
from .widgets import WidgetBase

class BibQueryGUI(WidgetBase):
    def __init__(self, parent, tag_data: DataTags, tag_total: DataTags):
        """
        file_path: path to the original paper
        """
        super().__init__()
        self.parent = parent
        self.init_tag_data = tag_data
        self.init_tag_total = tag_total
        self.initUI()
    
    def initUI(self):
        # self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setWindowTitle("Input bibtex and tag info")
        self.resize(420, 600)
        self.filename_lbl = QLabel()
        self.bib_edit = QTextEdit()
        self.bib_edit.setMinimumSize(300,200)
        self.insert_template_button = QPushButton("Use bibtex template")
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Canel")

        self.tag_prompt_lbl = QLabel("Edit tags for this file:")
        self.tag_edit = TagEditor(tag_data= self.init_tag_data, tag_total=self.init_tag_total)
        self.tag_edit.setMinimumSize(300, 200)


        main_box = QHBoxLayout()
        vlayout = QVBoxLayout()
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.ok_button)
        hlayout.addWidget(self.cancel_button)
        vlayout.addWidget(self.filename_lbl, 0)
        vlayout.addWidget(self.bib_edit, 1)
        vlayout.addWidget(self.insert_template_button, 0)
        vlayout.addLayout(hlayout, 0)

        vlayout_R = QVBoxLayout()
        vlayout_R.addWidget(self.tag_prompt_lbl)
        vlayout_R.addWidget(self.tag_edit)

        rframe = QFrame()
        rframe.setFrameStyle(QFrame.StyledPanel)
        rlayout = QVBoxLayout()
        rlayout.addWidget(rframe)
        rframe.setLayout(vlayout_R)

        main_box.addLayout(vlayout, 1)
        main_box.addWidget(rframe, 0)

        self.setLayout(main_box)


class BibQuery(BibQueryGUI):
    file_added = QtCore.pyqtSignal(str)     # send generated folder path
    add_to_pending = QtCore.pyqtSignal(str)   # send file_path
    def __init__(self, parent, file_path: typing.Union[str, None], tag_data: DataTags, tag_total:DataTags):
        """
        - file_path: Set to None for not providing file
        """
        super().__init__(parent, tag_data=tag_data, tag_total=tag_total)
        self.file_path = file_path
        self.db: DataBase

        if not self.file_path is None:
            file_name = os.path.split(self.file_path)[-1]
        else:
            file_name = "Anonymous"
        self.filename_lbl.setText(file_name)

        self.connectMethods()

    def setDatabase(self, db: DataBase):
        # Set database to inspect if file already exists
        self.db = db
    
    def connectMethods(self):
        self.ok_button.clicked.connect(self.confirm)
        self.cancel_button.clicked.connect(self.cancel)
        self.insert_template_button.clicked.connect(self.insertBibTemplate)
    
    def insertBibTemplate(self):
        with open(os.path.join(DOC_PATH, "bibTemplate.bib"), "r") as f:
            bib_template = f.read()
        bib_template = bib_template.replace("<Identifier>", sssUUID())
        self.bib_edit.setText(bib_template)

    def confirm(self):
        parser = BibParser(mode = "single")
        bib_txt = self.bib_edit.toPlainText()
        bib = parser(bib_txt)[0]
        tag_list = self.tag_edit.getSelectedTags().toOrderedList()
        fg = FileGenerator(
            file_path = self.file_path,
            title = bib["title"],
            year = bib["year"],
            authors = bib["authors"]
        )
        # Check if the file already exists
        for k, v in self.db.items():
            v: DataPoint
            t1 = v.bib["title"].lower()
            t2 = bib["title"].lower()
            similarity = difflib.SequenceMatcher(a = t1, b = t2).ratio()
            if similarity > 0.8:
                query_strs= [
                    "File may exists already",
                    "{year} - {title}".format(year = v.bib["year"], title = v.bib["title"]),
                    "FROM: {authors}".format(authors = "|".join(v.bib["authors"]))
                ]
                if not self.queryDialog(title = "File may exist", msg = "\n".join(query_strs)):
                    self.close()
                    return

        if not fg.generateDefaultFiles(data_dir=getConf()["database"]):
            self.add_to_pending.emit(self.file_path)
            self.close()
            return 

        dst_dir = fg.dst_dir
        fm = FileManipulator(dst_dir)
        fm.screen()
        fm.writeBib(bib_txt)
        fm.writeTags(tag_list)
        self.file_added.emit(dst_dir)
        self.close()
    
    def cancel(self):
        self.fail_add_bib.emit(self.file_path)
        self.close()
