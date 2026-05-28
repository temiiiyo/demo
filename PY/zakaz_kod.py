import os, sys

from PyQt6.QtQuickWidgets import QQuickWidget
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import pymysql
from zakaz import Ui_MainWindow

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, cart = None):
        super().__init__()
        self.setupUi(self)

        self.db = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            database='shveyka',
            cursorclass=pymysql.cursors.DictCursor
        )

        self.cursor = self.db.cursor()

        self.show_orders()


    def show_orders(self):
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(
            ['Номер заказа', 'Дата оформления', 'Статус', 'Сумма', 'Действие']
        )

        self.cursor.execute('''
        select o.id, o.order_date, o.status, 
        sum(p.price * oi.quantity) as total
        from product p
        join orders_items oi on oi.product_id = p.id
        join orders o on o.id = oi.orders_id
        group by o.id
        order by o.order_date;
        ''')

        for row, o in enumerate(self.cursor.fetchall()):
            self.tableWidget.insertRow(row)
            self.tableWidget.setItem(row, 0, QTableWidgetItem(str(o['id'])))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(str(o['order_date'])))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(o['status']))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(str(o['total'])))

            btn = QPushButton('Удалить заказ')
            btn.clicked.connect(lambda _, oid=o['id']: self.delete_order(oid))
            self.tableWidget.setCellWidget(row, 4, btn)

    def delete_order(self, oid):
        self.cursor.execute('delete from orders_items where orders_id = %s', (oid,))
        self.cursor.execute('delete from orders where id = %s', (oid,))
        self.db.commit()
        QMessageBox.information(self, 'ОК', 'Товар удален')
        self.show_orders()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())