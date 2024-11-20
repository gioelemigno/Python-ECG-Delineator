# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class MainWindow(QWidget):
     def __init__(self):
         super(MainWindow, self).__init__()
         self.resize(400, 300)
         self.setWindowTitle('Main Window')

         # Menu
         self.setContextMenuPolicy(Qt.CustomContextMenu)
         self.customContextMenuRequested.connect(self.right_menu)

     def right_menu(self, pos):
         menu = QMenu()

         # Add menu options
         hello_option = menu.addAction('Hello World')
         goodbye_option = menu.addAction('GoodBye')
         exit_option = menu.addAction('Exit')

         # Menu option events
         hello_option.triggered.connect(lambda: print('Hello World'))
         goodbye_option.triggered.connect(lambda: print('Goodbye'))
         exit_option.triggered.connect(lambda: exit())

         # Position
         menu.exec_(self.mapToGlobal(pos))


if __name__ == '__main__':
     app = QApplication([])
     window = MainWindow()
     window.show()
     sys.exit(app.exec_())
