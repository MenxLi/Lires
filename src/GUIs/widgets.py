
from PyQt5.QtWidgets import QStyle, QWidget, QMessageBox


class WidgetBase(QWidget):
    def warnDialog(self, messege, info_msg = ""):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText(messege)
        msg_box.setInformativeText(info_msg)
        msg_box.setWindowTitle("Warning")
        msg_box.setStandardButtons(QMessageBox.Ok)
        return msg_box.exec()
    
    def warnDialogCritical(self, messege, info_msg = "Please restart the program"):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText(messege)
        msg_box.setInformativeText(info_msg)
        msg_box.setWindowTitle("Critical warning")
        msg_box.setStandardButtons(QMessageBox.Ok)
        return msg_box.exec()
    
    def queryDialog(self, msg, title = "Query", func = lambda x: None):
        msg_box = QMessageBox()
        msg_box.setText(msg)
        msg_box.setWindowTitle(title)
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg_box.buttonClicked.connect(func)
        return_value = msg_box.exec()
        if return_value == QMessageBox.Ok:
            return True
        else: return False