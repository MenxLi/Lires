from __future__ import annotations
from typing import List
import json
from ..confReader import getConfV, saveToConf
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QPushButton, QComboBox
from PyQt6.QtCore import pyqtSignal

class ServerPresetEdit(QDialog):
	on_ok = pyqtSignal(list)
	def __init__(self, parent):
		super().__init__(parent = parent)
		self.initUI()

	def initUI(self):
		self.vlayout = QVBoxLayout()
		self.t_edit = QPlainTextEdit()
		self.btn_ok = QPushButton("OK")

		self.vlayout.addWidget(self.t_edit)
		self.vlayout.addWidget(self.btn_ok)
		self.setLayout(self.vlayout)

		preset_server: List[dict] = getConfV("server_preset")
		self.t_edit.textChanged.connect(self.onTextChange)
		self.btn_ok.clicked.connect(self.confirm)
		self.t_edit.setPlainText(json.dumps(preset_server, indent = 1))
	
	def confirm(self):
		t = self.t_edit.toPlainText()
		if self.checkSyntax(t):
			saveToConf(server_preset = json.loads(t))
			self.on_ok.emit(json.loads(t))
			self.close()
	
	def onTextChange(self):
		t = self.t_edit.toPlainText()
		self.btn_ok.setEnabled(self.checkSyntax(t))
	
	def checkSyntax(self, json_text) -> bool:
		try:
			preset = json.loads(json_text)
		except json.decoder.JSONDecodeError:
			return False
		if not isinstance(preset, list):
			return False
		preset: list[dict]
		for server in preset:
			if not isinstance(server, dict):
				return False
			for k in ["host", "port", "access_key"]:
				if not k in server:
					return  False
		return True

class ServerPresetChoice(QDialog):
	on_ok = pyqtSignal(dict)
	def __init__(self, parent):
		super().__init__(parent = parent)
		self.initUI()

	def initUI(self):
		self.vlayout = QVBoxLayout()
		self.btn_ok = QPushButton("OK")
		self.btn_cancel = QPushButton("Cancel")
		self.cb = QComboBox(self)

		preset_server: List[dict] = getConfV("server_preset")
		for server in preset_server:
			host = server["host"]
			port = server["port"]
			access_key = server["access_key"]

			show_str = "{}:{}".format(host, port)
			self.cb.addItem(show_str, userData=server)
		self.vlayout.addWidget(self.cb)
		hlayout = QHBoxLayout()
		hlayout.addWidget(self.btn_ok)
		hlayout.addWidget(self.btn_cancel)
		self.vlayout.addLayout(hlayout)
		self.setLayout(self.vlayout)

		self.btn_ok.clicked.connect(self.confirm)
		self.btn_cancel.clicked.connect(self.close)
	
	def confirm(self):
		self.on_ok.emit(self.cb.currentData())
		self.close()
