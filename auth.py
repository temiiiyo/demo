import os, sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from PY.auth import Ui_MainWindow
import pymysql

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.cart = {}

        self.db = pymysql.connect(
            host = 'localhost',
            user = 'root',
            password = 'root',
            database = 'shveyka',
            cursorclass = pymysql.cursors.DictCursor
        )
        self.cursor = self.db.cursor()
        self.open_logo()
        self.pushButton_login.clicked.connect(self.login)
        self.pushButton.clicked.connect(self.login_guest)


    def open_logo(self):
        pixmap = QPixmap(f'images/logo_sh.png')
        if not pixmap.isNull():
            self.label_logo.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            self.label_logo.setText('Нет Лого')

    def login(self):
        login = self.lineEdit_login.text().strip()
        password = self.lineEdit_password.text().strip()

        self.cursor.execute(
            'select id, login, role from users where login = %s and password = %s', (login, password)
        )
        user = self.cursor.fetchone()

        if user:
            role = user['role']
            QMessageBox.information(self, 'Успех', f'Добро пожаловать, {login}!')
            if role == 'admin':
                from admin import MainWindow
                self.admin_window = MainWindow()
                self.admin_window.show()
            elif role == 'manager':
                from manager import MainWindow
                self.manager_window = MainWindow()
                self.manager_window.show()
            elif role == 'client':
                from client import MainWindow
                self.client_window = MainWindow()
                self.client_window.show()
            else:
                QMessageBox.warning(self, 'Ошибка', 'Неверный логин или пароль')
        self.close()

    def login_guest(self):
        from guest import MainWindow
        self.guest_window = MainWindow()
        self.guest_window.show()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())