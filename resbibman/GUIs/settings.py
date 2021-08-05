import typing
import warnings
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QAbstractItemView, QCheckBox, QComboBox, QDialog, QFrame, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QPushButton, QTextEdit, QVBoxLayout, QWidget, QFileDialog
from PyQt5 import QtCore

from ..backend.dataClass import DataList, DataTableList

from .widgets import RefWidgetBase
from ..confReader import getConf, getConfV, getStyleSheets, saveToConf

class SubSettingsBase(RefWidgetBase):
	def __init__(self) -> None:
		super().__init__()
		self._frame = QFrame()
		self._layout = QVBoxLayout()
		self._layout.addWidget(self._frame)
		self.setLayout(self._layout)
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
		self._frame.setLayout(vbox)

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
			print("Database path saved, Database path set to: {}".format(getConf()["database"]))

class SetSortingMethod(SubSettingsBase):
	def initUI(self):
		self.cb = QComboBox(self)
		self.cb.addItems([DataList.SORT_AUTHOR, DataList.SORT_TIMEADDED, DataList.SORT_YEAR])
		self.cb.setCurrentText(getConf()["sort_method"])
		self.lbl = QLabel("Sort by: ")
		hbox = QHBoxLayout()
		hbox.addWidget(self.lbl)
		hbox.addWidget(self.cb)
		self._frame.setLayout(hbox)
	
	def confirm(self):
		selection = self.cb.currentText()
		if selection != getConf()["sort_method"]:
			saveToConf(sort_method = selection)
			self.getSelectPanel().data_model.sortBy(selection)
			print("Sorting method changed to {}". format(getConf()["sort_method"]))

class setTableHeader(SubSettingsBase):
	def initUI(self):
		vbox = QVBoxLayout()
		self.label = QLabel("Table header:")
		self.list_wid = QListWidget()
		for k in [DataTableList.HEADER_YEAR, DataTableList.HEADER_AUTHOR, DataTableList.HEADER_TITLE, DataTableList.HEADER_TIMEMODIFY]:
			box = QCheckBox(k)
			if k in getConfV("table_headers"):
				box.setChecked(True)
			item = QListWidgetItem(self.list_wid)
			self.list_wid.addItem(item)
			self.list_wid.setItemWidget(item, box)
		self.list_wid.setDragDropMode(QAbstractItemView.InternalMove)
		vbox.addWidget(self.label)
		vbox.addWidget(self.list_wid, 0)
		self._frame.setLayout(vbox)
	def confirm(self):
		# https://blog.csdn.net/sinat_34149445/article/details/94548871
		count = self.list_wid.count()  # 得到QListWidget的总个数
		cb_list = [self.list_wid.itemWidget(self.list_wid.item(i))
                  for i in range(count)]  # 得到QListWidget里面所有QListWidgetItem中的QCheckBox
		chooses = []  # 存放被选择的数据
		for cb in cb_list:  # type:QCheckBox
			if cb.isChecked():
				chooses.append(cb.text())
		saveToConf(table_headers = chooses)
		print("Headers changed -> {}".format(chooses))
		self.getMainPanel().reloadData()
		self.getSelectPanel().data_view.initSettings()	# Resize header width

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
		self._frame.setLayout(hbox)
	
	def confirm(self):
		selection = self.cb.currentText()
		if selection != getConf()["stylesheet"]:
			saveToConf(stylesheet = selection)
			app = QtWidgets.QApplication.instance()
			ss = getStyleSheets()[getConf()["stylesheet"]]
			if ss == "":
				app.setStyleSheet("")
			else:
				with open(ss, "r", encoding="utf-8") as f:
					app.setStyleSheet(f.read())
			print("Loaded new style: {}".format(getConf()["stylesheet"]))

class SettingsWidget(RefWidgetBase):
	def __init__(self, dialog_win) -> None:
		super().__init__(parent = dialog_win)
		self.parent = dialog_win 

	def init(self):
		self.sub_settings = [SetDatabase(), SetSortingMethod(), setTableHeader(), SetStyle()]
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

