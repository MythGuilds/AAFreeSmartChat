from PySide2.QtCore import QSize
from PySide2.QtWidgets import QMessageBox


def show_error(message: str, fixes: str):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)

    msg.setText("An error has occurred!")
    msg.setInformativeText(message)
    msg.setWindowTitle("Error")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.setDetailedText(fixes)
    retval = msg.exec_()
    print("value of pressed message box button:", retval)


def show_message(message: str, message2: str):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)

    msg.setText(message)
    msg.setInformativeText(message2)
    msg.setWindowTitle("Information")
    msg.setStandardButtons(QMessageBox.Ok)

    retval = msg.exec_()
    print("value of pressed message box button:", retval)
