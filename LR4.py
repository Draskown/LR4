#!/usr/bin/env python3
#-*- coding:utf-8 -*-


import sys, cv2, csv, numpy as np
from queue import PriorityQueue
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPalette, QColor, QPixmap, QFont, QImage
from PyQt5.QtWidgets import QApplication, QMainWindow


from random import randrange


BLACK = (0, 0, 0)
RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
WHITE = (255, 255, 255)
START = (223, 5, 227)
FINISH = (133, 4, 135)



class GUI(QMainWindow):
	def __init__(self):
		super(GUI, self).__init__()
		self.setGeometry(450, 200, 860, 600)
		self.setWindowTitle("LR4")
		
		self.image = cv2.imread("./Maps/1.png")
		self.line_draw = self.image.copy()
		self.draw_img = self.image.copy()
		
		self.grid = []
		self.path = []
		self.path_is_done = False
		
		self.setUI()
	
	
	class Node:
		def __init__(self, x, y, colour):
			self.x = x
			self.y = y
			self.colour = colour
			self.neighbours = []
			
		def get_pos(self):
			return self.x, self.y
			
		def is_closed(self):
			return self.colour == RED
			
		def is_open(self):
			return self.colour == GREEN
			
		def is_barrier(self):
			return self.colour == BLACK
			
		def is_start(self):
			return self.colour == START
			
		def is_finish(self):
			return self.colour == FINISH
			
		def update_neighbours(self, grid):
			self.neighbours = []
			
			# Down
			if self.y < 39 and not grid[self.x][self.y + 1].is_barrier():
				self.neighbours.append(grid[self.x][self.y + 1])
			#Up
			if self.y > 0 and not grid[self.x][self.y - 1].is_barrier():
				self.neighbours.append(grid[self.x][self.y - 1])
			# Left
			if self.x > 0 and not grid[self.x-1][self.y].is_barrier():
				self.neighbours.append(grid[self.x-1][self.y])
			# Right
			if self.x < 79 and not grid[self.x+1][self.y].is_barrier():
				self.neighbours.append(grid[self.x+1][self.y])


	def h(self, p1, p2):
		x1, y1 = p1
		x2, y2 = p2
		return abs(x1-x2) + abs(y1-y2)
		
		
	def setUI(self):
		self.pic_label = QtWidgets.QLabel(self)
		self.pic_label.setGeometry(30, 30, 800, 400)
		self.pic_label.setPixmap(QPixmap("./Maps/1.png"))
		self.pic_label.setScaledContents(True)
		
		self.start_but = QtWidgets.QPushButton(self)
		self.start_but.move(400, 500)
		self.start_but.setText("Start")
		self.start_but.adjustSize()
		self.start_but.clicked.connect(self.start)
		
		self.menubar = QtWidgets.QMenuBar(self)
		self.menubar.setGeometry(QtCore.QRect(0, 0, self.width(), 30))
		
		self.menuFile = QtWidgets.QMenu(self.menubar)
		self.menuFile.setTitle("File")
		
		self.actionOpen = QtWidgets.QAction(self)
		self.actionOpen.setText("Open map")
		self.actionOpen.setShortcut("Ctrl+O")
		self.actionOpen.triggered.connect(self.open_clicked)
		
		self.actionSave = QtWidgets.QAction(self)
		self.actionSave.setText("Save map")
		self.actionSave.setShortcut("Ctrl+S")
		self.actionSave.triggered.connect(self.save_clicked)
		
		self.actionClose = QtWidgets.QAction(self)
		self.actionClose.setText("Close app")
		self.actionClose.setShortcut("Ctrl+Q")
		self.actionClose.triggered.connect(self.close_clicked)
		
		self.actionSaveRun = QtWidgets.QAction(self)
		self.actionSaveRun.setText("Save run")
		self.actionSaveRun.setVisible(False)
		self.actionSaveRun.triggered.connect(self.save_run)
		
		self.menuFile.addAction(self.actionOpen)
		self.menuFile.addAction(self.actionSave)
		self.menuFile.addAction(self.actionClose)
		self.menuFile.addAction(self.actionSaveRun)
		self.menubar.addAction(self.menuFile.menuAction())	
		
		self.statusBar = QtWidgets.QStatusBar()
		self.setStatusBar(self.statusBar)
		
		s_pos = (160, 450)
		self.s_label = QtWidgets.QLabel(self)
		self.s_label.move(s_pos[0], s_pos[1])
		self.s_label.setText("Set starting position")
		self.s_label.adjustSize()
		
		self.s_x_label = QtWidgets.QLabel(self)
		self.s_x_label.move(s_pos[0]+8, s_pos[1]+30)
		self.s_x_label.setText("X:")
		
		self.s_x = QtWidgets.QSpinBox(self)
		self.s_x.setMaximum(79)
		self.s_x.move(self.s_x_label.x()+20, self.s_x_label.y())
		self.s_x.valueChanged.connect(self.draw_points)
		
		self.s_y_label = QtWidgets.QLabel(self)
		self.s_y_label.move(self.s_x_label.x(), self.s_x_label.y()+45)
		self.s_y_label.setText("Y:")
		
		self.s_y = QtWidgets.QSpinBox(self)
		self.s_y.setMaximum(39)
		self.s_y.move(self.s_x.x(), self.s_y_label.y())
		self.s_y.valueChanged.connect(self.draw_points)
		
		f_pos = (600, 450)
		self.f_label = QtWidgets.QLabel(self)
		self.f_label.move(f_pos[0], f_pos[1])
		self.f_label.setText("Set destination")
		self.f_label.adjustSize()
		
		self.f_x_label = QtWidgets.QLabel(self)
		self.f_x_label.move(f_pos[0]-6, f_pos[1]+30)
		self.f_x_label.setText("X:")
		
		self.f_x = QtWidgets.QSpinBox(self)
		self.f_x.setMaximum(79)
		self.f_x.move(self.f_x_label.x()+20, self.f_x_label.y())
		self.f_x.valueChanged.connect(self.draw_points)
		
		self.f_y_label = QtWidgets.QLabel(self)
		self.f_y_label.move(self.f_x_label.x(), self.f_x_label.y()+45)
		self.f_y_label.setText("Y:")
		
		self.f_y = QtWidgets.QSpinBox(self)
		self.f_y.setMaximum(39)
		self.f_y.move(self.f_x.x(), self.f_y_label.y())
		self.f_y.valueChanged.connect(self.draw_points)
	
	
	def mouseMoveEvent(self, e):
		self.line_draw = self.draw_img.copy()
		
		x = int((e.x() - 30) / 10.0)
		y = int((e.y() - 30) / 10.0)
		
		if y > 39 or x > 79 or x < 0 or y < 0:
			return
		
		self.line_draw[y, x] = (0, 0, 0)
		
		self.draw_points()
		
	
	def start(self):
		self.init_nodes()
		
		self.statusBar.clearMessage()
		
		for row in self.grid:
			for node in row:
				node.update_neighbours(self.grid)
		
		open_set = PriorityQueue()
		count = 0
		open_set.put((0, count, self.start_node))
		came_from = {}
		g_score = {node: float("inf") for row in self.grid for node in row}
		g_score[self.start_node] = 0
		f_score = {node: float("inf") for row in self.grid for node in row}
		f_score[self.start_node] = self.h(self.start_node.get_pos(), self.end_node.get_pos())
		
		open_set_hash = {self.start_node}
		
		while not open_set.empty():
			current = open_set.get()[2]
			open_set_hash.remove(current)
			
			if current == self.end_node:
				
				while current in came_from:
					current = came_from[current]
					self.path.append(current)
					current.colour = BLUE
				
				self.draw_points()
				self.path_is_done = True
				self.actionSaveRun.setVisible(True)
				return
				
			for neighbour in current.neighbours:
				temp_g_score = g_score[current] + 1
				
				if temp_g_score < g_score[neighbour]:
					came_from[neighbour] = current
					g_score[neighbour] = temp_g_score
					f_score[neighbour] = temp_g_score + self.h(neighbour.get_pos(), self.end_node.get_pos())
					if neighbour not in open_set_hash:
						count += 1
						open_set.put((f_score[neighbour], count, neighbour))
						open_set_hash.add(neighbour)
						neighbour.colour = GREEN
			
			if current != self.start:
				current.colour = RED
				
		self.statusBar.showMessage("Could not find exit")
		self.draw_points()


	def init_nodes(self):
		self.grid = []
		self.path = []
		self.start_node = None
		self.end_node = None
		self.path_is_done = False
		for x in range(80):
			self.grid.append([])
			for y in range(40):
					if x == self.s_x.value() and y == self.s_y.value():
						self.grid[x].append(self.Node(x, y, START))
						self.start_node = self.grid[x][y]
					elif x == self.f_x.value() and y == self.f_y.value():
						self.grid[x].append(self.Node(x, y, FINISH))
						self.end_node = self.grid[x][y]
					else:
						self.grid[x].append(self.Node(x, y, tuple(self.line_draw[y, x])))

	
	def save_clicked(self):
		fname = QtWidgets.QFileDialog.getSaveFileName(
			parent = self, 
			caption="Save file",
			directory="./Maps/",
			filter="Image (*.png *.jpg *.bmp);;Data file (*.csv)"
		)[0]
		
		if not fname:
			return
		
		cv2.imwrite(fname, self.line_draw)
		self.statusBar.showMessage('Map has been saved')


	def save_run(self):
		fname = QtWidgets.QFileDialog.getSaveFileName(
			parent = self, 
			caption="Save file",
			directory="./Maps/",
			filter="Data file (*.csv)"
		)[0]
		
		if not fname:
			return
			
		with open(fname, 'w') as file:
			writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			
			for i in range (len(self.path)):
				if self.path[i].x == 0:
					angle = 90
				else:
					angle = np.arctan(self.path[i].y / self.path[i].x)
				writer.writerow([str(i+1), str(self.path[i].x), str(self.path[i].y), str(angle)])
				
		self.statusBar.showMessage("Run has been saved")

		
	def open_clicked(self):
		fname = QtWidgets.QFileDialog.getOpenFileName(
			parent=self, 
			caption='Open image',
			directory='./Maps/',
			filter="Image (*.png *.jpg *.bmp);;Data file (*.csv)"
		)[0]
		
		if not fname:
			return
		
		if fname[-3:] != "csv":
			img = cv2.imread(fname)
			
			self.image = cv2.resize(img, (80, 40), interpolation=cv2.INTER_AREA)
			
			
		else:
			file = open(fname)
			file = np.loadtxt(file, delimiter=", ")
			
			self.image = np.ones(shape=(file.shape[0], file.shape[1], 3), dtype=np.uint8)
			
			for y in range (file.shape[0]):
				for x in range (file.shape[1]):
					if file[y, x] == 1:
						self.image[y, x] = (0,0,0)
					else:
						self.image[y, x] = (255, 255, 255)
		
		self.image = cv2.resize(self.image, (80, 40), interpolation=cv2.INTER_AREA)
		
		self.statusBar.showMessage("Map has been loaded")
		self.line_draw = self.image.copy()
		self.draw_img = self.image.copy()
		self.draw_points()
					

	
	def close_clicked(self):
		exit(0)	
	
	
	def draw_points(self):
		if self.path_is_done:
			self.grid = []
			self.actionSaveRun.setVisible(False)
			
		if self.s_y.value() == self.f_y.value():
			self.s_y.setValue = self.f_y.value()-1
		elif self.f_x.value() == self.f_x.value():
			self.s_x.setValue = self.f_x.value()-1
			
		self.draw_img = self.line_draw.copy()
		self.draw_img[self.s_y.value(), self.s_x.value()] = (223, 5, 227)
		self.draw_img[self.f_y.value(), self.f_x.value()] = (133, 4, 135)
		
		if len(self.grid) != 0:
			for row in self.grid:
				for node in row:
					if node.colour != WHITE and node.colour != BLACK:
						self.draw_img[node.get_pos()[1], node.get_pos()[0]] = node.colour
		
		self.display_img = cv2.cvtColor(self.draw_img, cv2.COLOR_BGR2RGB)		
		self.display_img = QImage(
			self.display_img, 
			self.display_img.shape[1], 
			self.display_img.shape[0],
			self.display_img.strides[0],
			QImage.Format_RGB888
		)
		
		self.pic_label.setPixmap(QPixmap.fromImage(self.display_img))



def setStyle(app):
	app.setStyle("Fusion")
	
	app.setFont(QFont("Gilroy", 11))
	dark_palette = QPalette()
	WHITE = QColor(255, 255, 255)
	BLACK = QColor(0, 0, 0)
	RED = QColor(255, 0, 0)
	PRIMARY = QColor(53, 53, 53)
	SECONDARY = QColor(25, 25, 25)
	LIGHT_PRIMARY = QColor(100, 100, 100)
	TERTIARY = QColor(42, 130, 218)
	dark_palette.setColor(QPalette.Window, PRIMARY)
	dark_palette.setColor(QPalette.WindowText, WHITE)
	dark_palette.setColor(QPalette.Base, SECONDARY)
	dark_palette.setColor(QPalette.AlternateBase, PRIMARY)
	dark_palette.setColor(QPalette.ToolTipBase, WHITE)
	dark_palette.setColor(QPalette.ToolTipText, WHITE)
	dark_palette.setColor(QPalette.Text, WHITE)
	dark_palette.setColor(QPalette.Button, LIGHT_PRIMARY)
	dark_palette.setColor(QPalette.ButtonText, WHITE)
	dark_palette.setColor(QPalette.BrightText, RED)
	dark_palette.setColor(QPalette.Link, TERTIARY)
	dark_palette.setColor(QPalette.Highlight, TERTIARY)
	dark_palette.setColor(QPalette.HighlightedText, BLACK)
	app.setPalette(dark_palette)
	app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")
	


if __name__ == '__main__':
	app = QApplication(sys.argv)
	setStyle(app)
	win = GUI()
	win.show()
	sys.exit(app.exec_())

