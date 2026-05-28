import os, sys
from PyQt6.QtQuickWidgets import QQuickWidget
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import pymysql

from auth import Ui_MainWindow
class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


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
        self.pushButton.clicked.connect(self.login_as_guest)

    def open_logo(self):
        pixmap = QPixmap(f'../images/logo_sh.png')
        if not pixmap.isNull():
            self.label_logo.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            self.label_logo.setText('Нет Лого')

    def login(self):
        """Авторизация пользователя"""
        login = self.lineEdit_login.text().strip()
        password = self.lineEdit_password.text().strip()

        # Поиск пользователя в базе данных
        self.cursor.execute(
            'select id, login, role from users where login = %s and password = %s',
            (login, password)
        )
        user = self.cursor.fetchone()

        if user:
            role = user['role']
            QMessageBox.information(self, 'Успех', f'Добро пожаловать, {login}!')
            if role == 'admin':
                self.open_admin_window()
            elif role == 'manager':
                self.open_manager_window()
            elif role == 'client':
                self.open_client_window()
            else:
                QMessageBox.warning(self, 'Ошибка', 'Неизвестная роль пользователя')
                return
            self.close()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Неверный логин или пароль')

    def login_as_guest(self):
        self.open_guest_window()
        self.close()

    def open_admin_window(self):
        from admin_temiy import MainWindow as AdminWindow
        self.admin_window = AdminWindow()
        self.admin_window.show()

    def open_manager_window(self):
        from manager_code import MainWindow as ManagerWindow
        self.manager_window = ManagerWindow()
        self.manager_window.show()


    def open_client_window(self):
        from client_code import MainWindow as ClientWindow
        self.client_window = ClientWindow()
        self.client_window.show()

    def open_guest_window(self):
        from guest_kod import MainWindow as GuestWindow
        self.guest_window = GuestWindow()
        self.guest_window.show()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())