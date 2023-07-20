import os, json
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont, QDesktopServices
from PyQt5.QtWidgets import (
	QLabel,
	QMainWindow,
	QDockWidget,
	QDialog,
	QHBoxLayout,
	QListWidget,
	QWidget,
	QVBoxLayout,
	QPushButton,
	QListWidgetItem,
	QStackedWidget,
	QFileDialog,
	QLayout,
	QAbstractItemView,
)

from version import *
from gui_utils import *

class C4DTag:
	def __init__(self, name: str) -> None:
		self.name: str = name

class TagsWindow(QDockWidget):
	def __init__(self, parent=None):
		super().__init__(parent)

		self.tags: list[C4DTag] = [
			C4DTag('Favorite'),
			C4DTag('Customer'),
			C4DTag('Package'),
		]

		self.setWindowTitle("Tags")
		self.setWindowFlags(self.windowFlags() & Qt.WindowCloseButtonHint)
		self.resize(400, 400)

		mainArea = QtWidgets.QScrollArea(self)
		mainArea.setWidgetResizable(True)

		widget = QtWidgets.QWidget(mainArea)
		widget.setMinimumWidth(50)

		layout = FlowLayout(widget)
		self.words = []
		for tag in self.tags:
			label = BubbleWidget(tag.name)
			label.setFont(QtGui.QFont('SblHebrew', 18))
			label.setFixedWidth(label.sizeHint().width())
			layout.addWidget(label)

		mainArea.setWidget(widget)
		# self.setCentralWidget(mainArea)
		self.setWidget(mainArea)