import sys
from PySide6 import QtWidgets, QtCore
import resouce
import google.generativeai as genai
from dotenv import load_dotenv
import os
import system_comments
import speak
import unicodedata
import threading

class CommentWindow(QtWidgets.QWidget):
    def __init__(self, text: str, screen):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        layout = QtWidgets.QVBoxLayout()
        comment = QtWidgets.QTextBrowser()
        comment.setPlainText(text)
        layout.addWidget(comment)
        self.setLayout(layout)
        self.adjustSize()
        self.setStyleSheet("QWidget { border: 2px solid blue; }")
        self.setGeometry(
            screen.width()-self.width(),
            screen.height()-self.height(),
            self.width(), self.height())
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.close)
        self.timer.start(10000)
        self.thread = threading.Thread(target=speak.Speak().speak, args=(self.clean_text(text),))
        self.thread.start()
        self.thread.join()
    def clean_text(self, text):
        normalized_text = unicodedata.normalize('NFKC', text)
        return ''.join(c for c in normalized_text if unicodedata.category(c)[0] != 'C')

class CommandWindow(QtWidgets.QWidget):
    def __init__(self, model):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.commandedit = QtWidgets.QTextEdit(self)
        self.commandedit.setPlaceholderText("会話文を入力")
        self.button = QtWidgets.QPushButton("話す", self)
        self.exitbutton = QtWidgets.QPushButton("終了", self)
        self.button.clicked.connect(self.speak)
        self.exitbutton.clicked.connect(self.clickexit)
        layout = QtWidgets.QHBoxLayout()
        buttons = QtWidgets.QVBoxLayout()
        layout.addWidget(self.commandedit)
        buttons.addWidget(self.button)
        buttons.addWidget(self.exitbutton)
        layout.addLayout(buttons)
        self.setLayout(layout)
        self.adjustSize()
        self.chat = model.start_chat(history=[])
        self.comment_window = None
        self.screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
        self.setGeometry(
            self.screen.width()-self.width()-300,
            self.screen.height()-300,
            self.width(), self.height())
        self.image_window = ImageWindow(self.screen)
        self.image_window.show()
    def tostring(self, arg: list):
        c = str()
        for line in arg:
            c += line + "\n"
        return c
    @QtCore.Slot()
    def speak(self):
        try:
            response = self.chat.send_message(self.commandedit.toPlainText())
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "error!", str(e))
            sys.exit(1)
        lines = response.text.splitlines()
        last = lines[-1] if lines else ""
        if last in "笑顔":
            self.image_window.setImage("0000")
            self.comment_window = CommentWindow(self.tostring(lines[:-1]), self.screen)
        elif last in "目閉じ":
            self.image_window.setImage("0001")
            self.comment_window = CommentWindow(self.tostring(lines[:-1]), self.screen)
        elif last in "ジト目":
            self.image_window.setImage("0002")
            self.comment_window = CommentWindow(self.tostring(lines[:-1]), self.screen)
        elif last in "微笑み":
            self.image_window.setImage("0003")
            self.comment_window = CommentWindow(self.tostring(lines[:-1]), self.screen)
        elif last in "怒り":
            self.image_window.setImage("0004")
            self.comment_window = CommentWindow(self.tostring(lines[:-1]), self.screen)
        elif last in "泣き":
            self.image_window.setImage("0005")
            self.comment_window = CommentWindow(self.tostring(lines[:-1]), self.screen)
        elif last in "驚き":
            self.image_window.setImage("0006")
            self.comment_window = CommentWindow(self.tostring(lines[:-1]), self.screen)
        elif last in "愛情":
            self.image_window.setImage("0007")
            self.comment_window = CommentWindow(self.tostring(lines[:-1]), self.screen)
        elif last in "焦り":
            self.image_window.setImage("0008")
            self.comment_window = CommentWindow(self.tostring(lines[:-1]), self.screen)
        elif last in "落ち込み":
            self.image_window.setImage("0009")
            self.comment_window = CommentWindow(self.tostring(lines[:-1]), self.screen)
        elif last in "困惑":
            self.image_window.setImage("0010")
            self.comment_window = CommentWindow(self.tostring(lines[:-1]), self.screen)
        elif last in "赤面":
            self.image_window.setImage("0011")
            self.comment_window = CommentWindow(self.tostring(lines[:-1]), self.screen)
        else:
            QtWidgets.QMessageBox.warning(self, "error", response.text)
            sys.exit(1)
        self.comment_window.show()
    @QtCore.Slot()
    def clickexit(self):
        reply = QtWidgets.QMessageBox.question(
            self,
            "確認",
            "アプリケーションを終了しますか？",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            sys.exit()


class ImageWindow(QtWidgets.QWidget):
    def __init__(self, screen):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.image = QtWidgets.QLabel(self)
        self.image.setStyleSheet("QLabel { image: url(:/image/0000.png); }")
        self.image.setScaledContents(True)
        self.image.resize(300, 450)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.image)
        self.setLayout(layout)
        self.resize(300, 450)
        self.setGeometry(
            screen.width()-self.width(),
            screen.height()-self.height(),
            self.width(), self.height())
    def setImage(self, image: str):
        self.image.setStyleSheet(f"QLabel {{ image: url(:/image/{image}.png); }}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    load_dotenv('environ.env')
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-pro", system_instruction=system_comments.system_instruction)
    image = CommandWindow(model)
    image.show()
    sys.exit(app.exec())
