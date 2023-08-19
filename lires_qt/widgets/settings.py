from __future__ import annotations
from abc import abstractmethod
from typing import Dict, List
import warnings, os, shutil, time
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QAbstractItemView, QCheckBox, QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout, QFileDialog

from lires.core.dataClass import DataList, DataTableList
from lires.confReader import getConf, getConfV, saveToConf, TMP_DB

from ._styleUtils import isThemeDarkMode
from .widgets import RefWidgetBase
from .serverPreset import ServerPresetEdit, ServerPresetChoice

from ..config import getStyleSheets

class SubSettingsBase(RefWidgetBase):
	def __init__(self) -> None:
		super().__init__()
		self._frame = QFrame()
		self._frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)

		self._layout = QVBoxLayout()
		self._layout.addWidget(self._frame)
		self._layout.setContentsMargins(0,0,0,0)
		self.setLayout(self._layout)

		self._request_restart = False
		self._request_restart_is_critical = False
		self.initUI()

	@abstractmethod
	def initUI(self):
		raise NotImplementedError("The initUI method for {} is not implemented yet".format(self.__class__.__name__))

	@property
	def frame(self):
		return self._frame

	def confirm(self):
		warnings.warn("The confim method for {} is not implemented yet".format(self.__class__.__name__))
	
	def requestRestart(self, is_critical = False):
		self._request_restart = True
		self._request_restart_is_critical = is_critical
	
	def CONFIRM(self):
		self.confirm()
		if self._request_restart:
			if self._request_restart_is_critical:
				self.warnDialogCritical(messege = "Some changes not applied", \
							info_msg = "Please restart the program")
			else:
				self.warnDialog(messege = "Some changes not applied", \
								info_msg = "Please consider restarting the program")

class SetDatabase(SubSettingsBase):
	"""
	Set both database and remote server
	"""
	def initUI(self):
		self.label_db = QLabel("Database path (offline/server):")
		self.line_edit_db = QLineEdit(self)
		self.btn = QPushButton("Choose")
		vbox = QVBoxLayout()
		hbox = QHBoxLayout()
		hbox.addWidget(self.line_edit_db, 1)
		hbox.addWidget(self.btn, 0)
		vbox.addWidget(self.label_db)
		vbox.addLayout(hbox)

		self.label_host = QLabel("Lires server settings:")
		self.btn_preset_edit = QPushButton("Edit preset")
		self.btn_preset_choose = QPushButton("Choose preset")
		self.lbl_host = QLabel("host: ")
		self.line_edit_host = QLineEdit(self)
		self.lbl_port = QLabel("port: ")
		self.line_edit_port = QLineEdit(self)
		self.lbl_key = QLabel("access key: ")
		self.line_edit_key = QLineEdit(self)
		self.line_edit_key.setEchoMode(QLineEdit.EchoMode.Password)
		hbox1 = QHBoxLayout()
		hbox2 = QHBoxLayout()
		hbox3 = QHBoxLayout()
		vbox.addWidget(self.label_host)
		hbox1.addWidget(self.lbl_host, 0)
		hbox1.addWidget(self.line_edit_host, 2)
		hbox2.addWidget(self.lbl_port, 0)
		hbox2.addWidget(self.line_edit_port, 1)
		hbox2.addWidget(self.lbl_key, 0)
		hbox2.addWidget(self.line_edit_key, 1)
		hbox3.addWidget(self.btn_preset_edit)
		hbox3.addWidget(self.btn_preset_choose)
		vbox.addLayout(hbox1)
		vbox.addLayout(hbox2)
		vbox.addLayout(hbox3)

		self.frame.setLayout(vbox)

		self.line_edit_host.textChanged.connect(self.activateWidgets)
		self.btn.clicked.connect(self.chooseDir)
		self.btn_preset_edit.clicked.connect(self.openPresetEdit)
		self.btn_preset_choose.clicked.connect(self.openPresetChoice)

		self.line_edit_db.setText(getConf()["database"])
		self.line_edit_host.setText(getConfV("host"))
		self.line_edit_port.setText(getConfV("port"))
		self.line_edit_key.setText(getConfV("access_key"))
	
	def openPresetEdit(self):
		self.preset_edit = ServerPresetEdit(self)
		self.preset_edit.show()

	def openPresetChoice(self):
		self.preset_choice = ServerPresetChoice(self)
		def _setChoice(choice: dict):
			self.line_edit_host.setText(str(choice["host"]))
			self.line_edit_port.setText(str(choice["port"]))
			self.line_edit_key.setText(str(choice["access_key"]))
		self.preset_choice.on_ok.connect(_setChoice)
		self.preset_choice.show()
	
	def activateWidgets(self, host_line: str):
		"""
		check if host has been set.
		if host is set, inactivate database path
		otherwise, inactivate port
		"""
		self.line_edit_db.setEnabled(not bool(host_line))
		self.line_edit_port.setEnabled(bool(host_line))
		self.line_edit_key.setEnabled(bool(host_line))

	def chooseDir(self):
		file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
		if file != "":
			self.line_edit_db.setText(file)
	
	def confirm(self):
		database_path = self.line_edit_db.text()
		host = self.line_edit_host.text()
		port = self.line_edit_port.text()
		access_key = self.line_edit_key.text()
		RELOAD = False

		main_window = self.getMainPanel()
		if not database_path == getConf()["database"]:
			saveToConf(database = database_path)
			self.logger.debug("Database path saved, Database path set to: {}".format(getConf()["database"]))
			RELOAD = True
		
		if not host == getConf()["host"] or not port == getConf()["port"]:
			if not (host == "" or host.startswith("http://") or host.startswith("https://")):
				self.warnDialog("Invalid host address, please check.")
				return
			saveToConf(host = host, port = port)
			self.logger.debug("LiresWeb host set to: {}:{}".format(host, port))
			self.logger.info("Server settings changed, deleting previous local temporary files")
			main_window.releaseDatabaseResources()
			for f in os.listdir(TMP_DB):
				f_path = os.path.join(TMP_DB, f)
				if os.path.isfile(f_path):
					os.remove(f_path)
				if os.path.isdir(f_path):
					shutil.rmtree(f_path)
				self.logger.info("Local temporary files deleted, reloading database from server...")
			RELOAD = True
		
		if not access_key == getConf()["access_key"]:
			saveToConf(access_key = access_key)
			self.logger.debug("LiresWeb access key changed.")
			RELOAD = True

		if RELOAD:
			self.logger.info("Database settings changed.")
			# Dont know if necessary to sleep
			# add to test if loading empty config will still happen, if settings changed
			time.sleep(0.5) 
			main_window.reloadData()

class SetSortingMethod(SubSettingsBase):
	def initUI(self):
		self.cb = QComboBox(self)
		self.cb.addItems([DataList.SORT_AUTHOR, DataList.SORT_TIMEADDED, DataList.SORT_YEAR])
		self.cb.setCurrentText(getConf()["sort_method"])
		
		self.ck = QCheckBox("Reverse", self)
		self.ck.setChecked(getConf()["sort_reverse"])

		self.lbl = QLabel("Sort by: ")
		hbox = QHBoxLayout()
		hbox.addWidget(self.lbl, 1)
		hbox.addWidget(self.ck, 0)
		hbox.addWidget(self.cb, 1)
		self.frame.setLayout(hbox)
	
	def confirm(self):
		selection = self.cb.currentText()
		reverse = self.ck.isChecked()
		if selection != getConf()["sort_method"] or reverse != getConf()["sort_reverse"]:
			saveToConf(sort_method = selection, sort_reverse = reverse)
			self.getSelectPanel().data_model.sortBy(selection, reverse = reverse)
			self.logger.info("Sorting method changed to {} (Reverse: {})"\
					.format(getConf()["sort_method"], getConf()["sort_reverse"]))

class SetTableHeader(SubSettingsBase):
	def initUI(self):
		self.old_headers = getConfV("table_headers")
		vbox = QVBoxLayout()
		self.label = QLabel("Table header:")
		self.list_wid = QListWidget()
		header_candidate = [
				DataTableList.HEADER_FILESTATUS,
				DataTableList.HEADER_YEAR, 
				DataTableList.HEADER_AUTHOR, 
				DataTableList.HEADER_TITLE, 
				DataTableList.HEADER_TIMEMODIFY]
		for k in header_candidate:
			box = QCheckBox(k)
			if k in self.old_headers:
				box.setChecked(True)
			item = QListWidgetItem(self.list_wid)
			self.list_wid.addItem(item)
			self.list_wid.setItemWidget(item, box)
		self.list_wid.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
		vbox.addWidget(self.label)
		vbox.addWidget(self.list_wid, 0)
		self.frame.setLayout(vbox)

	def confirm(self):
		# https://blog.csdn.net/sinat_34149445/article/details/94548871
		count = self.list_wid.count()  # 得到QListWidget的总个数
		cb_list = [self.list_wid.itemWidget(self.list_wid.item(i))
                  for i in range(count)]  # 得到QListWidget里面所有QListWidgetItem中的QCheckBox
		chooses = []  # 存放被选择的数据
		for cb in cb_list:  # type:QCheckBox
			if cb.isChecked():
				chooses.append(cb.text())
		if chooses != self.old_headers:
			saveToConf(table_headers = chooses)
			self.logger.info("Headers changed -> {}".format(chooses))
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
		self.frame.setLayout(hbox)
	def confirm(self):
		_dark = isThemeDarkMode()

		selection = self.cb.currentText()
		if selection != getConf()["stylesheet"]:
			saveToConf(stylesheet = selection)
			app:QtWidgets.QApplication = QtWidgets.QApplication.instance()
			ss = getStyleSheets()[getConf()["stylesheet"]]
			if ss == "":
				app.setStyleSheet("")
			else:
				with open(ss, "r", encoding="utf-8") as f:
					app.setStyleSheet(f.read())
			self.logger.info("Loaded new style: {}".format(getConf()["stylesheet"]))
			if _dark != isThemeDarkMode():
				self.requestRestart()

class SetFont(SubSettingsBase):
	def initUI(self):
		hlayout = QHBoxLayout()
		hlayout.addWidget(QLabel("Fonts: "), 1)
		vlayout = QVBoxLayout()
		hlayout.addLayout(vlayout, 2)
		self.lbls: List[QLabel] = []
		self.inpts: List[QLineEdit] = []
		for k in getConfV("font_sizes").keys():
			lbl = QLabel(f"{k}")
			inpt = QLineEdit(self)
			self.lbls.append(lbl)
			self.inpts.append(inpt)
			font, size = getConfV("font_sizes")[k]
			inpt.setText(f"{font}, {size}")
			_hlayout = QHBoxLayout()
			_hlayout.addWidget(lbl)
			_hlayout.addWidget(inpt)
			vlayout.addLayout(_hlayout)
		self.frame.setLayout(hlayout)
	
	def confirm(self):
		font_sizes: Dict[str, list] = {}
		try:
			for lbl, inpt in zip(self.lbls, self.inpts):
				k = lbl.text()
				v = inpt.text()
				font, size = v.split(", ")
				font = font.strip()
				size = int(size.strip())
				font_sizes[k] = [font, size]
		except ValueError:
			self.warnDialog("An error happened while parsing font settings, \
				   please check the format.")
			return
		if getConfV("font_sizes") != font_sizes:
			#  self.requestRestart()
			saveToConf(font_sizes = font_sizes)
			self.getMainPanel().loadFontConfig()


class SetAutoSaveComments(SubSettingsBase):
	def initUI(self):
		self.cb = QCheckBox("Auto save comments")
		hbox = QHBoxLayout()
		hbox.addWidget(self.cb)
		self._frame.setLayout(hbox)
		if getConfV("auto_save_comments"):
			self.cb.setChecked(True)
	
	def confirm(self):
		status = self.cb.isChecked()
		if status != getConfV("auto_save_comments"):
			saveToConf(auto_save_comments = status)
			self.requestRestart()
			if status:
				self.logger.info("Autosave comments enabled.")
			else:
				self.logger.info("Autosave comments disabled.")

class SettingsWidget(RefWidgetBase):
	def __init__(self, dialog_win) -> None:
		super().__init__(parent = dialog_win)
		self.parent = dialog_win 

	def init(self):
		self.sub_settings = [
			SetDatabase(), 
			SetSortingMethod(), 
			SetStyle(),
			SetAutoSaveComments(),
			SetFont(),
			SetTableHeader(), 
		]
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
			i.CONFIRM()
		self.parent.close()

