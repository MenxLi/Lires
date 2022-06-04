import typing, os, shutil, warnings
from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QListView, QVBoxLayout, QInputDialog
from PyQt6.QtGui import QAction

from .widgets import RefWidgetBase
from ..core.utils import openFile
from ..core.pdfTools import getPDFCoverAsQPixelmap
from ..confReader import ICON_PATH, getConfV


class PendingWindowGUI(RefWidgetBase):
	
	def __init__(self) -> None:
		super().__init__()
		self.initUI()
		self.initActions()
		self.setAcceptDrops(True)
	
	def initUI(self):
		self.setWindowTitle("Pending files")
		self.file_model = PFileListModel([])
		self.file_view = QListView()
		self.file_view.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.ActionsContextMenu)
		self.file_view.setModel(self.file_model)

		self.cover_label = QLabel()
		self.cover_label.setScaledContents(True)
		self.cover_label.setMinimumSize(50, 100)
		self.resize(800, 600)

		vbox = QVBoxLayout()
		hbox = QHBoxLayout()
		hbox.addWidget(self.file_view, 1)
		hbox.addWidget(self.cover_label, 1)

		vbox.addWidget(QLabel(self, text="Blow are files without bib info."))
		vbox.addLayout(hbox)
		self.setLayout(vbox)
		self._center()
	
	def initActions(self):
		self.act_rename_file = QAction("Rename", self)
		self.act_rename_file.setShortcut(QtGui.QKeySequence("F2"))
		self.act_delete_file = QAction("Delete", self)
		self.act_delete_file.setShortcut(QtGui.QKeySequence("Del"))
		self.act_add_info = QAction("Add information", self)
		self.act_add_info.setShortcut(QtGui.QKeySequence("Space"))

		self.file_view.addAction(self.act_add_info)
		self.file_view.addAction(self.act_rename_file)
		self.file_view.addAction(self.act_delete_file)

class PendingWindow(PendingWindowGUI):
	PENDING_FOLDER = "pending"
	def __init__(self) -> None:
		super().__init__()
		self.ppath = os.path.join(getConfV("database"), self.PENDING_FOLDER)
		if not os.path.exists(self.ppath):
			os.mkdir(self.ppath)
		self.loadData()
		self.connectFuncs()
	
	def connectFuncs(self):
		self.act_add_info.triggered.connect(self.addInfo)
		self.act_rename_file.triggered.connect(self.renameCurrentSelection)
		self.act_delete_file.triggered.connect(self.deleteCurrentSelections)
		self.file_view.doubleClicked.connect(self.doubleClickOnEntry)
		self.file_view.selectionModel().currentChanged.connect(self.onRowChanged)
	
	def _updateCover(self, fpath):
		if fpath is None or not fpath.endswith(".pdf"):
			self.cover_label.setScaledContents(False)
			cover = QtGui.QPixmap(os.path.join(ICON_PATH, "cloud-24px.svg"))
		else:
			self.cover_label.setScaledContents(True)
			cover = getPDFCoverAsQPixelmap(fpath)
		self.cover_label.setPixmap(cover)
	
	def onRowChanged(self, current, previous):
		row = current.row()
		fpath = self.file_model.datalist[row]
		self._updateCover(fpath)

	def loadData(self):
		pend_files = [os.path.join(self.ppath, f) for f in os.listdir(self.ppath)]	
		self.pend_files = [i for i in pend_files if self.checkExtension(i)]
		self.file_model.assignData(pend_files)
	
	def doubleClickOnEntry(self):
		fpath = self.getCurrentSelection(return_multiple=False)
		openFile(fpath)
	
	def addFilesToPendingDataBaseByURL(self, urls: typing.List[str]):
		for f in urls:
			self._addFile(f)
		self.loadData()
	
	def _addFile(self, fpath):
		if self.checkExtension(fpath):
			_file_name = os.path.split(fpath)[-1]
			new_fpath = os.path.join(self.ppath, _file_name)
			if not os.path.exists(new_fpath):
				shutil.copy2(fpath, self.ppath)
			else:
				self.warnDialog("The file exists in the pending folder!", new_fpath)
			self.loadData()
			return new_fpath
		return None
	
	def addInfo(self):
		urls = self.getCurrentSelection(return_multiple=True)
		self.getMainPanel().addFilesToDatabaseByURL(urls)
		return urls
	
	def renameCurrentSelection(self):
		fpath = self.getCurrentSelection(return_multiple=False)
		_file_name = os.path.split(fpath)[-1]
		file_name, file_extension = os.path.splitext(_file_name)
		text, ok = QInputDialog.getText(self, "Edit name for {}".format(file_name), "(extension: {})".format(file_extension), text = file_name)
		if ok:
			new_fpath = os.path.join(self.ppath, text+file_extension)
			if not os.path.exists(new_fpath):
				os.rename(fpath, new_fpath)
				self.loadData()
				return True
			else:
				self.warnDialog("The file exists", "Rename failed. ")
				return False
		return False
	
	def deleteCurrentSelections(self):
		urls = self.getCurrentSelection(return_multiple=True)
		if self.queryDialog("Delete {} file(s)?".format(len(urls))):
			for fpath in urls:
				os.remove(fpath)
			self.loadData()
			return True
		return False

	def checkExtension(self, fpath):
		try:
			_file_name = os.path.split(fpath)[-1]
		except:
			return False
		file_name, file_extension = os.path.splitext(_file_name)
		if not file_extension in getConfV("accepted_extensions"):
			warnings.warn("Incorrect file type, check extensions.")
			return False
		else:
			return True

	def dragEnterEvent(self, a0: QtGui.QDragEnterEvent) -> None:
		if a0.mimeData().hasUrls():
			a0.accept()
		else:
			a0.ignore()
		return super().dragEnterEvent(a0)
    
	def dropEvent(self, a0: QtGui.QDropEvent) -> None:
		files = [u.toLocalFile() for u in a0.mimeData().urls()]
		self.addFilesToPendingDataBaseByURL(files)
		return super().dropEvent(a0)

	def getCurrentSelection(self, return_multiple = False) -> typing.Union[None, str, typing.List[str]]:
		indexes = self.file_view.selectedIndexes()
		if not indexes:
			return None
		try:
			all_data = [self.file_model.datalist[index.row()] for index in indexes]
		except:
			# When index is larger than the length of the data
			return None

		if return_multiple:
			return all_data
		else:
			return all_data[0]

class PFileListModel(QtCore.QAbstractListModel):
	delete_current_selected = QtCore.pyqtSignal()
	def __init__(self, file_list: typing.List[str]) -> None:
		super().__init__()
		self.datalist = file_list
	
	def data(self, index, role):
		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			fpath = self.datalist[index.row()]
			try:
				_file_name = os.path.split(fpath)[-1]
				file_name, file_extension = os.path.splitext(_file_name)
				return file_name
			except:
				pass
    
	def rowCount(self, index) -> int:
		return len(self.datalist)
    
	def add(self, fpath: str):
		self.datalist.append(fpath)
		self.layoutChanged.emit()

	def assignData(self, filelist: typing.List[str]):
		self.datalist = filelist
		self.layoutChanged.emit()
