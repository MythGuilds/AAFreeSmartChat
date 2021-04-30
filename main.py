import sqlite3
import sys
from os import path
from datetime import datetime

from PySide2 import QtWidgets
from PySide2.QtCore import QTimer, QUrl, Qt, QSize, QEvent
from PySide2.QtGui import QFont
import PySide2.QtGui
from PySide2.QtWidgets import QApplication, QWidget, QTextEdit, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QMenuBar, \
    QToolBar, QToolButton, QSizePolicy, QMainWindow, QSizeGrip
from PySide2.QtWebEngineWidgets import QWebEngineView
import qdarkstyle
from datetime_matcher import DatetimeMatcher
import types
from googletrans import Translator

fileModded = []
file_path = r"D:\Users\Mitchell\Documents\AAFreeTo\ChatLogs\\"

database_path = "data.db"
closing = False
message_index = 0
canResize = False
masterLedger = []
start_translate = False
userLanguage = "en"

# Bug Report
# Error when day switches. New chat file isn't created on games end unless a restart of the client is performed
# Program skips first message in file

class AppRef:
    def __init__(self):
        self.DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'


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
        self.autoTransButton = QPushButton("Automatic")
        self.manualTransButton = QPushButton("Manual")
        self.closeTransButton = QPushButton("Close")
        self.closeTransButton.setDisabled(True)

        self.drag_label = QLabel("")

        self.translate_label = QLabel("Translate")
        self.translate_label.setAlignment(Qt.AlignCenter)
        self.translate_label.setFont(QFont('Arial', 13))
        self.translate_label.setMargin(8)

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://translate.google.com/"))

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
        toolBar.addWidget(settingsToolButton)

        exitToolButton = QToolButton()
        exitToolButton.setText("Exit")
        exitToolButton.clicked.connect(self.forceQuit)
        toolBar.addWidget(exitToolButton)

        toolBar.layout()

        layout2 = QHBoxLayout()

        # layout2.addWidget(self.autoTransButton)
        # layout2.addWidget(self.manualTransButton)
        # layout2.addWidget(self.closeTransButton)
        layout.addLayout(layout2)
        layout.addWidget(self.browser)
        self.setLayout(layout)

        self.browser.setVisible(False)

        self.closeTransButton.clicked.connect(self.close_trans_clicked)
        self.manualTransButton.clicked.connect(self.manual_trans_clicked)

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

    def translateMessage(self, message):
        global userLanguage
        translator = Translator()
        lang = translator.detect(message).lang

        if type(lang) != str:
            lang = userLanguage

        print("Language: " + lang)

        if lang == userLanguage:
            print("No trans")
            return message

        return translator.translate(message, dest=userLanguage, src=lang).text
        print("trans")

    def watch_file(self):
        global file_path
        global message_index
        global masterLedger
        global start_translate

        today = str(datetime.today().date())
        file = open(file_path + today + '.log', encoding='utf8', mode='r')
        nonempty_lines = [line.strip("\n") for line in file if line != "\n"]
        file.close()
        line_count = len(nonempty_lines)

        if message_index < line_count:
            file = open(file_path + today + '.log', encoding='utf8', mode='r')
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
                    message.type = "[" + chat_type + "]:"
                    break
            message.type = "Whisper" if message.type is None else message.type

            message.content = message.content.strip()



            # self.sysFunctions.db_connection.execute("INSERT INTO MESSAGES (DATE, CHANNEL, PLAYER, MESSAGE) \
            #       VALUES ('%s', '%s', '%s', '%s')" % ())
            # self.sysFunctions.db_connection.commit()

            # Break down message strings to insert values into database, add time


            if not start_translate:
                message.display_text = message.type + " " + message.content
            else:
                message.display_text = message.type + " " + self.translateMessage(message.content)

            if message_index > 0:
                old_message = masterLedger[-1].display_text
                if old_message != message.display_text:
                    print(message.display_text)
                    self.textEdit.append(message.display_text)
                    self.textEdit.moveCursor(PySide2.QtGui.QTextCursor.End)

            masterLedger.append(message)
            message_index += 1

        file.close()
        # if not start_translate:
        #     print("Testing translate")
        #     print(self.translateMessage("Привет"))
        start_translate = True


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
        self.closeTransButton.setDisabled(True)
        self.manualTransButton.setDisabled(False)
        # self.resize(500, 400)

    def manual_trans_clicked(self):
        self.browser.setVisible(True)
        self.closeTransButton.setDisabled(False)
        self.manualTransButton.setDisabled(True)
        # self.resize(500, 700)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    win = Application()
    win.show()
    sys.exit(app.exec_())
