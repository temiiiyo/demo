import os, sys

from PyQt6.QtQuickWidgets import QQuickWidget
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import pymysql
from korzina import Ui_MainWindow

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, cart = None):
        super().__init__()
        self.setupUi(self)

        self.cart = cart if cart is not None else {}

        self.db = pymysql.connect(
            host = 'localhost',
            user = 'root',
            password = 'root',
            database = 'shveyka',
            cursorclass = pymysql.cursors.DictCursor
        )

        self.cursor = self.db.cursor()

        self.show_cart()
        self.pushButton_2.clicked.connect(self.back_main)
        self.pushButton.clicked.connect(self.check_out)

    def show_cart(self):
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(
            ['Товар', 'Цена', 'Количество', 'Сумма']
        )

        total =  0
        row = 0

        for pid, qty in self.cart.items():
            self.cursor.execute('select name, price from product where id = %s', (pid,))
            p = self.cursor.fetchone()
            if p:
                summ = p['price'] * qty
                total += summ

                self.tableWidget.insertRow(row)
                self.tableWidget.setItem(row, 0, QTableWidgetItem(p['name']))
                self.tableWidget.setItem(row, 1, QTableWidgetItem(str(p['price'])))
                self.tableWidget.setItem(row, 2, QTableWidgetItem(str(qty)))
                self.tableWidget.setItem(row, 3, QTableWidgetItem(str(summ)))
                row += 1

        self.tableWidget.insertRow(row)
        self.tableWidget.setItem(row, 2, QTableWidgetItem('Итого:'))
        self.tableWidget.setItem(row, 3, QTableWidgetItem(str(total)))


    def back_main(self):
        self.close()

    def check_out(self):
        self.cursor.execute('insert into orders (order_date, status) values (now(), "новый")')
        oid = self.cursor.lastrowid

        for pid, q in self.cart.items():
            self.cursor.execute('select price from product where id = %s', (pid,))
            product = self.cursor.fetchone()
            if product:
                price = product['price']
                self.cursor.execute('insert into orders_items (orders_id, product_id, quantity, price) values (%s, %s, %s, %s)', (oid, pid, q, price))
        self.db.commit()
        self.cart.clear()
        QMessageBox.information(self, 'Успешно', f'Заказ {oid} создан')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())