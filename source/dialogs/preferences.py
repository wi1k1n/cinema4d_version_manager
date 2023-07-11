import sys
from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (
	QApplication, QLabel, QMainWindow, QMenu, QMenuBar, QToolBar, QAction, QSpinBox, QHBoxLayout, QListWidget, QWidget
)

class PreferencesWindow(QMainWindow):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle("Preferences")
		self.resize(400, 300)
		
		list = QListWidget()
		list.setMinimumWidth(100)
		list.addItem("General")
		list.addItem("Search paths")
		list.setFixedSize(list.sizeHintForColumn(0) + 2 * list.frameWidth() + 4, list.height())

		label = QLabel("Hello, World")

		layout = QHBoxLayout()
		layout.addWidget(list)
		layout.addWidget(label)

		widget = QWidget()
		widget.setLayout(layout)
		self.centralWidget = widget
		# self.centralWidget.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
		self.setCentralWidget(self.centralWidget)
