import os
import webbrowser
from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QDialog, QMessageBox
from .widgets import WidgetBase
from ..core.utils import openFile
from ..confReader import DOC_PATH, WEBPAGE


LICENSE = """
BSD 2-Clause License

Copyright (c) 2021-2022, Mengxun Li
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""

class HelpWidget(QDialog, WidgetBase):
    def __init__(self,*args,**kwargs):
        super(HelpWidget, self).__init__(*args,**kwargs)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.btn_manual = QPushButton("Manual")
        self.btn_manual.clicked.connect(self.openManual)

        self.btn_license = QPushButton("License")
        self.btn_license.clicked.connect(self.openLicense)

        self.btn_webpage = QPushButton("Webpage")
        self.btn_webpage.clicked.connect(self.openWebpage)

        layout.addWidget(self.btn_manual)
        layout.addWidget(self.btn_webpage)
        layout.addWidget(self.btn_license)
        self.setLayout(layout)

    def openManual(self):
        help_file_path = os.path.join(DOC_PATH, "UserGuide.md")
        openFile(help_file_path)
        self.close()

    def openLicense(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setText("LICENSE")
        msg_box.setInformativeText(LICENSE)
        msg_box.setWindowTitle("license")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
        self.close()

    def openWebpage(self):
        webbrowser.open(WEBPAGE)
        self.close()