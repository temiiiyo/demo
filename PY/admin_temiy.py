import os, sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import pymysql

from admin_interface import Ui_MainWindow

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
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scrollAreaWidgetContents.setLayout(self.scroll_layout)

        self.comboBox_sort.addItem('Все категории', None)
        self.cursor.execute('select id, name from category')
        for c in self.cursor.fetchall():
            self.comboBox_sort.addItem(c['name'], c['id'])

        self.load_product()

        self.lineEdit_search.textChanged.connect(self.load_product)
        self.comboBox_sort.currentIndexChanged.connect(self.load_product)

        self.pushButton_3.clicked.connect(self.open_korzina)
        self.pushButton_2.clicked.connect(self.open_zakaz)
        self.pushButton.clicked.connect(self.logout)

    def clear_product(self):
        while self.scroll_layout.count():
            w = self.scroll_layout.takeAt(0).widget()
            if w:
                w.deleteLater()

    def load_product(self):
        self.clear_product()

        query = '''
        select p.id, c.name as cat, p.name as p_name, pr.name as pr_name, p.price, p.photo_path, p.current_discount
        from product p
        join category c on c.id = p.category_id
        join proizvoditel pr on pr.id = p.proizvoditel_id
        where 1 = 1
        '''
        params = []

        if self.lineEdit_search.text():
            query += ' and p.name like %s'
            params.append(f'%{self.lineEdit_search.text()}%')
        if self.comboBox_sort.currentData():
            query += ' and p.category_id = %s'
            params.append(self.comboBox_sort.currentData())

        self.cursor.execute(query, params)

        for p in self.cursor.fetchall():
            self.scroll_layout.addWidget(self.create_card(p))

    def create_card(self, p):
        card = QFrame()
        layout = QHBoxLayout(card)

        photo = QLabel()
        photo.setFixedSize(120, 120)
        photo_path = p.get('photo_path', '')
        pixmap = QPixmap(f'images/{photo_path}')
        if not pixmap.isNull():
            photo.setPixmap(pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            photo.setText('Нет фото')
        layout.addWidget(photo)

        info = QVBoxLayout()
        info.addWidget(QLabel(f'<b>{p["p_name"]}</b>'))
        info.addWidget(QLabel(p['cat']))
        info.addWidget(QLabel(p['p_name']))
        info.addWidget(QLabel(f'{p["price"]} руб.'))
        layout.addLayout(info)

        if p.get('current_discount', 0) > 0:
            info.addWidget(QLabel(f"<font color = 'red' > Скидка: {p['current_discount']}%</font>"))

        btn = QPushButton('В корзину')
        btn.clicked.connect(lambda _, pid = p['id']: self.add_to_cart(pid))
        layout.addWidget(btn)

        return card

    def add_to_cart(self, pid):
        self.cart[pid] =self.cart.get(pid, 0) + 1
        QMessageBox.information(self, 'Ок', 'Товар добавлен в корзину')

    def open_korzina(self):
        from korzina_kod import MainWindow
        self.korzina_window = MainWindow(self.cart)
        self.korzina_window.show()

    def open_zakaz(self):
        from zakaz_kod import MainWindow
        self.zakaz_window = MainWindow()
        self.zakaz_window.show()

    def logout(self):
        from auth_kod import MainWindow
        self.auth_window = MainWindow()
        self.auth_window.show()
        window.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())