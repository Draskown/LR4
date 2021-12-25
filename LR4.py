#!/usr/bin/env python3
#-*- coding:utf-8 -*-


import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow



class GUI(QMainWindow):
	def __init__(self):
		super(GUI, self).__init__()
		self.setGeometry(200, 200, 300, 300)
		self.setWindowTitle("LR4")
		self.setUI()
		
		
	def setUI(self):
		self.label = QtWidgets.QLabel(self)
		self.label.setText("Label 1")
		self.label.move(50,50)
		
		self.b1 = QtWidgets.QPushButton(self)
		self.b1.clicked.connect(self.clicked)
		
		
	def clicked(self):
		self.label.setText("Fuck")
		self.update
		
		
	def update(self):
		self.label.adjustSize()


if __name__ == '__main__':
	app = QApplication(sys.argv)
	win = GUI()
	win.show()
	sys.exit(app.exec_())

