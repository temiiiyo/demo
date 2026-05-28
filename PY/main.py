import os, sys
from PyQt6.QtWidgets import *
from PyQt6.QtWidgets import QMessageBox, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from interface import Ui_MainWindow
import mysql.connector

class StoreApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.user_id = None
        self.user_role = None
        self.cart = {}

        self.db = mysql.connector.connect(
            host = 'localhost',
            user = 'root',
            password = 'root',
            database = 'odezda'
        )
        self.cursor = self.db.cursor(dictionary=True)

        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scrollAreaWidgetContents.setLayout(self.scroll_layout)
        self.stackedWidget.setCurrentIndex(3)


        self.pushButton_logout.clicked.connect(self.logout)
        self.pushButton_login.clicked.connect(self.login)
        self.pushButton_login_guest.clicked.connect(self.login_guest)
        self.pushButton_korzina.clicked.connect(self.show_cart)



        self.comboBox_cat.addItem('Все категории', None)
        self.cursor.execute('select id, name from category')
        for c in self.cursor.fetchall():
            self.comboBox_cat.addItem(c['name'], c['id'])

        self.comboBox_man.addItem('Все производители', None)
        self.cursor.execute('select id, name from manufacture')
        for m in self.cursor.fetchall():
            self.comboBox_man.addItem(m['name'], m['id'])

        self.comboBox_sort.addItems([
            'По названию', 'По цене(убыв.)', 'По цене(возр.)'
        ])

        self.lineEdit_search.textChanged.connect(self.load_product)
        self.comboBox_cat.currentIndexChanged.connect(self.load_product)
        self.comboBox_man.currentIndexChanged.connect(self.load_product)
        self.comboBox_sort.currentIndexChanged.connect(self.load_product)
        self.checkBox_disc.stateChanged.connect(self.load_product)
        self.pushButton_back_client.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.pushButton_back_zakaz.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.pushButton_oformit.clicked.connect(self.checkout)
        self.pushButton_zakaz.clicked.connect(self.show_orders)




    def login(self):
        self.cursor.execute('select id, fio, role from users where login = %s and password = %s', (self.lineEdit_login.text(), self.lineEdit_password.text()))
        user = self.cursor.fetchone()

        if user:
            self.user_id = user['id']
            self.user_role = user['role']
            self.label_fio.setText(user['fio'])
            self.pushButton_zakaz.setVisible(self.user_role == 'manager')
            self.load_product()
            self.stackedWidget.setCurrentIndex(0)
        else:
            QMessageBox.warning(self, 'Ошибка', 'Неверный логин или пароль')

    def login_guest(self):
        self.user_id = None
        self.user_role = None
        self.label_fio.setText('Гость')
        self.pushButton_zakaz.setVisible(False)
        self.pushButton_korzina.setVisible(False)
        self.load_product()
        self.stackedWidget.setCurrentIndex(0)

    def logout(self):
        self.user_id = None
        self.user_role = None
        self.stackedWidget.setCurrentIndex(3)

    def clear_product(self):
        while self.scroll_layout.count():
            w = self.scroll_layout.takeAt(0).widget()
            if w:
                w.deleteLater()


    def load_product(self):
        self.clear_product()

        query = '''
        select p.*, c.name as cat, m.name as man
        from product p 
        join category c on c.id = p.category_id
        join manufacture m on m.id = p.manufacture_id
        where 1 = 1
        '''
        params = []

        if self.lineEdit_search.text():
            query += ' and p.name like %s'
            params.append(f"%{self.lineEdit_search.text()}%")
        if self.comboBox_cat.currentData():
            query += ' and p.category_id = %s'
            params.append(self.comboBox_cat.currentData())
        if self.comboBox_man.currentData():
            query += ' and p.manufacture_id = %s'
            params.append(self.comboBox_man.currentData())
        if self.checkBox_disc.isChecked():
            query += ' and p.discount > 0'

        sort = self.comboBox_sort.currentText()
        if sort == 'По цене(убыв.)':
            query += ' order by p.price'
        elif sort == 'По цене(возр.)':
            query += ' order by p.price desc'
        else:
            query += ' order by p.name'

        self.cursor.execute(query, params)

        for p in self.cursor.fetchall():
            self.scroll_layout.addWidget(self.create_card(p))

    def create_card(self, p):
        card = QFrame()
        layout = QHBoxLayout(card)

        photo = QLabel()
        photo.setFixedSize(120, 120)
        pixmap = QPixmap(p['photo_path'])
        if not pixmap.isNull():
            photo.setPixmap(pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            photo.setText('Нет фото')
        layout.addWidget(photo)

        info = QVBoxLayout()
        info.addWidget(QLabel(f"<b>{p['name']}</b>"))
        info.addWidget(QLabel(p['cat']))
        info.addWidget(QLabel(p['man']))
        info.addWidget(QLabel(f"{p['price']} руб."))
        layout.addLayout(info)

        if self.user_role == 'client':
            btn = QPushButton('Добавить в корзину')
            btn.clicked.connect(lambda _, pid=p['id']: self.add_to_cart(pid))
            layout.addWidget(btn)

        return card

    def add_to_cart(self, pid):
        self.cart[pid] = self.cart.get(pid, 0) + 1
        QMessageBox.information(self, 'Ок', 'Товар добавлен в корзину')

    def show_cart(self):
        self.tableWidget_korzina.setRowCount(0)
        self.tableWidget_korzina.setColumnCount(4)
        self.tableWidget_korzina.setHorizontalHeaderLabels([
            'Товар', 'Цена', 'Количество', 'Сумма'
        ])

        total = 0
        row = 0

        for pid, qty in self.cart.items():
            self.cursor.execute('select name, price from product where id = %s', (pid,))
            p = self.cursor.fetchone()
            if p:
                summ = p['price'] * qty
                total += summ

                self.tableWidget_korzina.insertRow(row)
                self.tableWidget_korzina.setItem(row, 0, QTableWidgetItem(p['name']))
                self.tableWidget_korzina.setItem(row, 1, QTableWidgetItem(str(p['price'])))
                self.tableWidget_korzina.setItem(row, 2, QTableWidgetItem(str(qty)))
                self.tableWidget_korzina.setItem(row, 3, QTableWidgetItem(str(summ)))
                row += 1

        self.tableWidget_korzina.insertRow(row)
        self.tableWidget_korzina.setItem(row, 2, QTableWidgetItem('ИТОГО:'))
        self.tableWidget_korzina.setItem(row, 3, QTableWidgetItem(str(total)))
        self.stackedWidget.setCurrentIndex(1)

    def checkout(self):
        self.cursor.execute('insert into orders (user_id, order_date, status) values (%s, now(), "новый")', (self.user_id,))
        oid = self.cursor.lastrowid

        for pid, q in self.cart.items():
            self.cursor.execute('insert into orders_items (order_id, product_id, quantity) values (%s, %s, %s)', (oid, pid, q))
        self.db.commit()
        self.cart.clear()
        QMessageBox.information(self, 'Успешно', f'Заказ {oid} создан')


    def show_orders(self):
        if self.user_role != 'manager':
            return

        self.tableWidget_zakaz.setRowCount(0)
        self.tableWidget_zakaz.setColumnCount(6)
        self.tableWidget_zakaz.setHorizontalHeaderLabels([
            'Номер заказа', 'Клиент', 'Дата', 'Статус', 'Сумма', 'Действие'
        ])

        self.cursor.execute('''
        select o.id, u.fio, o.order_date, o.status, 
        sum(p.price * oi.quantity) as total 
        from product p 
        join orders_items oi on oi.product_id = p.id
        join orders o on o.id = oi.order_id 
        join users u on u.id = o.user_id
        group by o.id
        order by o.order_date;
        ''')

        for row, o in enumerate(self.cursor.fetchall()):
            self.tableWidget_zakaz.insertRow(row)
            self.tableWidget_zakaz.setItem(row, 0, QTableWidgetItem(str(o['id'])))
            self.tableWidget_zakaz.setItem(row, 1, QTableWidgetItem(o['fio']))
            self.tableWidget_zakaz.setItem(row, 2, QTableWidgetItem(str(o['order_date'])))
            self.tableWidget_zakaz.setItem(row, 3, QTableWidgetItem(o['status']))
            self.tableWidget_zakaz.setItem(row, 4, QTableWidgetItem(str(o['total'])))

            btn = QPushButton('Удалить заказ')
            btn.clicked.connect(lambda _, oid=o['id']: self.delete_order(oid))
            self.tableWidget_zakaz.setCellWidget(row, 5, btn)

        self.stackedWidget.setCurrentIndex(2)


    def delete_order(self, oid):
        self.cursor.execute('delete from orders_items where order_id = %s', (oid,))
        self.cursor.execute('delete from orders where id = %s', (oid,))
        self.db.commit()
        QMessageBox.information(self, 'Ок', 'Товар удален')
        self.show_orders()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StoreApp()
    window.show()
    sys.exit(app.exec())