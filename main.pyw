import os.path
import sqlite3
import sys
from os import path
from datetime import datetime
from datetime import timedelta

from PySide2 import QtWidgets
from PySide2.QtCore import QTimer, QUrl, Qt, QEvent
from PySide2.QtGui import QFont
import PySide2.QtGui
from PySide2.QtWidgets import QApplication, QWidget, QTextEdit, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, \
    QToolBar, QToolButton, QSizePolicy, QMainWindow, QSizeGrip
from PySide2.QtWebEngineWidgets import QWebEngineView
import qdarkstyle
from datetime_matcher import DatetimeMatcher
import types

import popups

fileModded = []

database_path = "data.db"
closing = False
message_index = 0
canResize = False
masterLedger = []
index_reset = True


class SysFunctions:
    def __init__(self):
        self.db_connection = None
        self.messageDataset = []

    def loadDB(self):
        global database_path
        global message_index
        if not path.exists(database_path):
            conn = sqlite3.connect(database_path)
            print("Opened database successfully")

            conn.execute('''CREATE TABLE MESSAGES
                     (ID INTEGER PRIMARY KEY   AUTOINCREMENT,
                     DATE           DATE       NOT NULL,
                     CHANNEL        TEXT       NOT NULL,
                     PLAYER         TEXT       NOT NULL,
                     MESSAGE        TEXT       NOT NULL
                     );''')

            print("Table created successfully")
        else:
            conn = sqlite3.connect(database_path)
        self.db_connection = conn
        cur = self.db_connection.cursor()
        cur.execute("SELECT * FROM MESSAGES WHERE DATE= '%s'" % (str(datetime.today().date())))

        self.messageDataset = cur.fetchall()

        message_index = len(self.messageDataset)
        for row in self.messageDataset:
            print(row)


class Application(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        global file_path
        file_path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder')
        file_path = file_path.replace("/", "\\") + "\\"
        self.setWindowTitle("AAFree Smart Chat")

        self.resize(500, 400)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        self.installEventFilter(self)

        self.setWindowOpacity(1.0)

        self.textEdit = QTextEdit()
        self.textEdit.setFont(QFont('Arial', 10))
        self.textEdit.setReadOnly(True)
        self.openTransButton = QPushButton("Translate")
        self.pauseTransButton = QPushButton("Pause Chat")
        self.closeTransButton = QPushButton("Close")
        self.closeTransButton.setDisabled(True)

        self.drag_label = QLabel("")

        self.translate_label = QLabel("Translate")
        self.translate_label.setAlignment(Qt.AlignCenter)
        self.translate_label.setFont(QFont('Arial', 13))
        self.translate_label.setMargin(8)

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://translate.google.com/"))

        self.chatIsPaused = False

        layout = QVBoxLayout()
        toolBar = QToolBar()

        toolBarSpacer = QWidget()
        toolBarSpacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        toolBar.addWidget(toolBarSpacer)

        layout.addWidget(toolBar)
        layout.addWidget(self.drag_label)
        layout.addWidget(self.textEdit)
        # layout.addWidget(self.translate_label)

        settingsToolButton = QToolButton()
        settingsToolButton.setText("Settings")
        # toolBar.addWidget(settingsToolButton)

        exitToolButton = QToolButton()
        exitToolButton.setText("Exit")
        exitToolButton.clicked.connect(self.forceQuit)
        toolBar.addWidget(exitToolButton)

        toolBar.layout()

        layout2 = QHBoxLayout()

        layout2.addWidget(self.openTransButton)
        layout2.addWidget(self.pauseTransButton)
        layout2.addWidget(self.closeTransButton)

        layout.addLayout(layout2)

        self.setLayout(layout)
        layout.addWidget(self.browser)
        self.browser.setVisible(False)

        self.closeTransButton.clicked.connect(self.close_trans_clicked)
        self.pauseTransButton.clicked.connect(self.pause_chat_clicked)
        self.openTransButton.clicked.connect(self.manual_trans_clicked)

        self.timer = QTimer()
        self.timer.timeout.connect(self.watch_file)

        self.timer.start(1000)

        self.gripSize = 16
        self.grips = []
        for i in range(4):
            grip = QSizeGrip(self)
            grip.resize(self.gripSize, self.gripSize)
            self.grips.append(grip)

    def forceQuit(self):
        app.quit()

    def resizeEvent(self, event):
        global canResize
        QMainWindow.resizeEvent(self, event)
        rect = self.rect()
        # top left grip doesn't need to be moved...
        # top right
        self.grips[1].move(rect.right() - self.gripSize, 0)
        # bottom right
        self.grips[2].move(
            rect.right() - self.gripSize, rect.bottom() - self.gripSize)
        # bottom left
        self.grips[3].move(0, rect.bottom() - self.gripSize)
        canResize = True

    def mousePressEvent(self, event):
        self.offset = event.pos()
        global canResize
        if canResize:
            canResize = False

    def mouseReleaseEvent(self, event):
        global canResize
        if canResize:
            canResize = False

    def mouseMoveEvent(self, event):
        global canResize
        x = event.globalX()
        y = event.globalY()

        if hasattr(self, 'offset'):
            x_w = self.offset.x()
            y_w = self.offset.y()
            if not canResize:
                self.move(x - x_w, y - y_w)

    def eventFilter(self, object, event):
        if event.type() == QEvent.WindowActivate:
            self.setWindowOpacity(1.0)
        elif event.type() == QEvent.WindowDeactivate:
            self.setWindowOpacity(0.5)
        elif event.type() == QEvent.FocusIn:
            self.setWindowOpacity(1.0)
        elif event.type() == QEvent.FocusOut:
            self.setWindowOpacity(0.5)

        return False

    def watch_file(self):

        if self.chatIsPaused: return None
        global index_reset
        global file_path
        global message_index
        global masterLedger

        today = datetime.today().date()
        yesterday = today - timedelta(days=1)

        if os.path.isfile(file_path + str(today) + '.log'):
            file = open(file_path + str(today) + '.log', encoding='utf8', mode='r')
            nonempty_lines = [line.strip("\n") for line in file if line != "\n"]
            file.close()
            if index_reset:
                print("Date reset")
                message_index = 0
                index_reset = False
        elif os.path.isfile(file_path + str(yesterday) + '.log'):
            file = open(file_path + str(yesterday) + '.log', encoding='utf8', mode='r')
            nonempty_lines = [line.strip("\n") for line in file if line != "\n"]
            file.close()
            index_reset = True
            today = yesterday
        else:
            self.hide()
            popups.show_error("Could not find a log file to parse.",
                              "Fixes: \n\n- Make sure you selected the correct directory\n\n- Try restarting you game client and launcher")
            return None

        line_count = len(nonempty_lines)

        if message_index < line_count:
            file = open(file_path + str(today) + '.log', encoding='utf8', mode='r')
            content = file.readlines()
        while message_index < line_count:
            message = types.SimpleNamespace()
            message.raw_message = content[message_index]
            datetime_matcher = DatetimeMatcher()

            message.datetime = datetime_matcher.extract_datetime("%Y-%m-%d %H:%M:%S", message.raw_message)

            message.type = None

            try:
                x = message.raw_message.split("]: ", 1)

                message.content = x[1]
            except IndexError:
                try:
                    x = message.raw_message.split("] to you:", 1)
                    message.content = x[1]
                    message.type = datetime_matcher.sub("%Y-%m-%d %H:%M:%S", "", x[0], 1)
                    message.type = message.type.replace(" | ", "")
                    message.type += "] to you: "
                    message.type = message.type.strip()

                except IndexError:
                    raise Exception("Invalid message format. Chat type could not be parsed.")

            chat_types = ["Local", "Party", "Raid", "Guild", "Family", "Faction", "Shout", "Trade", "Need Party",
                          "Command", "Trial", "Nation", " | To ["]

            for chat_type in chat_types:
                if x[0].find(chat_type) != -1:
                    if chat_type == " | To [":
                        message.type = datetime_matcher.sub("%Y-%m-%d %H:%M:%S", "", x[0], 1)
                        message.type = message.type.replace(" | ", "")
                        message.type += "]:"
                        break
                    message.type = datetime_matcher.sub("%Y-%m-%d %H:%M:%S", "", x[0], 1)
                    message.type = message.type.replace(" | ", "")
                    remove_str = "[" + chat_type + ": "
                    message.type = message.type.replace(remove_str, "")

                    message.type = "[" + chat_type + ": " + message.type + "]:"
                    break
            message.type = "Whisper" if message.type is None else message.type

            message.content = message.content.strip()

            # self.sysFunctions.db_connection.execute("INSERT INTO MESSAGES (DATE, CHANNEL, PLAYER, MESSAGE) \
            #       VALUES ('%s', '%s', '%s', '%s')" % ())
            # self.sysFunctions.db_connection.commit()

            # Break down message strings to insert values into database, add time

            message.display_text = message.type + " " + message.content

            if message_index > 0:
                old_message = masterLedger[-1].display_text
                if old_message != message.display_text:
                    print(message.display_text)
                    self.textEdit.append(message.display_text)
                    self.textEdit.moveCursor(PySide2.QtGui.QTextCursor.End)
            if message_index == 0:
                if message.raw_message:
                    print(message.display_text)
                    self.textEdit.append(message.display_text)
                    self.textEdit.moveCursor(PySide2.QtGui.QTextCursor.End)

            masterLedger.append(message)
            message_index += 1

        file.close()

    def closeEvent(self, event):
        global closing
        closing = True

        self.timer.stop()
        self.sysFunctions.db_connection.close()
        event.accept()  # let the window close

    def addMessages(self):
        global fileModded
        if len(fileModded) > 0:
            fileModded.pop()
            self.textEdit.setPlainText("")

    def close_trans_clicked(self):
        self.browser.setVisible(False)
        self.textEdit.setVisible(True)
        self.closeTransButton.setDisabled(True)
        # self.pauseTransButton.setDisabled(False)
        self.openTransButton.setDisabled(False)
        self.resize(500, 400)

    def pause_chat_clicked(self):
        if self.chatIsPaused:
            self.chatIsPaused = False
            self.pauseTransButton.setText("Pause Chat")
        else:
            self.chatIsPaused = True
            self.pauseTransButton.setText("Unpause Chat")

    def manual_trans_clicked(self):
        self.browser.setVisible(True)
        # self.textEdit.setVisible(False)
        self.closeTransButton.setDisabled(False)
        # self.pauseTransButton.setDisabled(True)
        self.openTransButton.setDisabled(True)
        self.resize(500, 700)


def prepend_line(file_name, line):
    """ Insert given string as a new line at the beginning of a file """
    # define name of temporary dummy file
    dummy_file = file_name + '.bak'
    # open original file in read mode and dummy file in write mode
    with open(file_name, 'r') as read_obj, open(dummy_file, 'w') as write_obj:
        # Write given line to the dummy file
        write_obj.write(line + '\n')
        # Read lines from original file one by one and append them to the dummy file
        for line in read_obj:
            write_obj.write(line)
    # remove original file
    os.remove(file_name)
    # Rename dummy file as the original file
    os.rename(dummy_file, file_name)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    popups.show_message("Please select your aafree log folder at:                              ", "<b>Documents -> AAFreeTo -> ChatLogs</b>")
    win = Application()
    win.show()
    sys.exit(app.exec_())
