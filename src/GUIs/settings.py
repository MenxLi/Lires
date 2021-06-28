import typing
import warnings
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QComboBox, QDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget, QFileDialog
from PyQt5 import QtCore

from ..backend.dataClass import DataList

from .widgets import RefWidgetBase
from ..confReader import getConf, getStyleSheets, saveToConf

class SubSettingsBase(RefWidgetBase):
	def __init__(self) -> None:
		super().__init__()
		self.initUI()

	def initUI(self):
		raise NotImplementedError("The initUI method for {} is not implemented yet".format(self.__class__.__name__))
	def confirm(self):
		warnings.warn("The confim method for {} is not implemented yet".format(self.__class__.__name__))

class SetDatabase(SubSettingsBase):
	def initUI(self):
		self.label = QLabel("Database path:")
		self.line_edit = QLineEdit(self)
		self.line_edit.setText(getConf()["database"])
		self.btn = QPushButton("Choose")
		vbox = QVBoxLayout()
		hbox = QHBoxLayout()
		hbox.addWidget(self.line_edit, 1)
		hbox.addWidget(self.btn, 0)
		vbox.addWidget(self.label)
		vbox.addLayout(hbox)
		self.setLayout(vbox)

		self.btn.clicked.connect(self.chooseDir)

	def chooseDir(self):
		file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
		if file != "":
			self.line_edit.setText(file)
	
	def confirm(self):
		database_path = self.line_edit.text()
		if not database_path == getConf()["database"]:
			saveToConf(database = database_path)
			self.getMainPanel().loadData(database_path)
			print("Database path saved.")

class SetSortingMethod(SubSettingsBase):
	def initUI(self):
		self.cb = QComboBox(self)
		self.cb.addItems([DataList.SORT_AUTHOR, DataList.SORT_TIMEADDED, DataList.SORT_YEAR])
		self.cb.setCurrentText(getConf()["sort_method"])
		self.lbl = QLabel("Sort by: ")
		hbox = QHBoxLayout()
		hbox.addWidget(self.lbl)
		hbox.addWidget(self.cb)
		self.setLayout(hbox)
	
	def confirm(self):
		selection = self.cb.currentText()
		if selection != getConf()["sort_method"]:
			saveToConf(sort_method = selection)
			self.getSelectPanel().data_model.sortBy(selection)
			print("Sorting method changed")

class SetStyle(SubSettingsBase):
	def initUI(self):
		ss_dict = getStyleSheets()
		self.cb = QComboBox(self)
		self.cb.addItems(list(ss_dict.keys()))
		self.cb.setCurrentText(getConf()["stylesheet"])
		self.lbl = QLabel("Application style: ")
		hbox = QHBoxLayout()
		hbox.addWidget(self.lbl)
		hbox.addWidget(self.cb)
		self.setLayout(hbox)
	
	def confirm(self):
		selection = self.cb.currentText()
		if selection != getConf()["stylesheet"]:
			saveToConf(stylesheet = selection)
			app = QtWidgets.QApplication.instance()
			ss = getStyleSheets()[getConf()["stylesheet"]]
			if ss == "":
				app.setStyleSheet("")
			else:
				with open(ss, "r") as f:
					app.setStyleSheet(f.read())
			print("Loaded new style")

class SettingsWidget(RefWidgetBase):
	def __init__(self, dialog_win) -> None:
		super().__init__(parent = dialog_win)
		self.parent = dialog_win 

	def init(self):
		self.sub_settings = [SetDatabase(), SetSortingMethod(), SetStyle()]
		for subsetting in self.sub_settings:
			subsetting.setMainPanel(self.getMainPanel())
			subsetting.setInfoPanel(self.getInfoPanel())
			subsetting.setSelectPanel(self.getSelectPanel())
			subsetting.setTagPanel(self.getTagPanel())
		self._initUI()

	def _initUI(self):
		layout = QVBoxLayout()

		self.btn_confirm = QPushButton("Ok")
		self.btn_cancel = QPushButton("Cancel")
		confirm_box = QHBoxLayout()
		confirm_box.addWidget(self.btn_confirm)
		confirm_box.addWidget(self.btn_cancel)

		for setting_wid in self.sub_settings:
			layout.addWidget(setting_wid)
		layout.addLayout(confirm_box)

		self.setLayout(layout)

		self.btn_cancel.clicked.connect(self.parent.close)
		self.btn_confirm.clicked.connect(self.confirm)

	def connectFuncs(self):
		pass

	def confirm(self):
		for i in self.sub_settings:
			i.confirm()
		self.parent.close()

