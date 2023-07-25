import os, json, typing, json
from functools import partial

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, QUrl, QRect, QPoint, QTimer, QSize, pyqtSignal, QByteArray
from PyQt5.QtGui import QFont, QDesktopServices, QMouseEvent, QShowEvent, QPaintEvent, QPainter, QColor, QPalette, QPen
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
	QColorDialog,
	QFormLayout,
	QLineEdit,
	QDialogButtonBox,
	QSizePolicy,
	QAction,
	QLayoutItem,
	QScrollArea
)

from version import *
from gui_utils import *
from utils import *

class FilterSortWindow(QDockWidget):
	def __init__(self, parent=None):
		super().__init__(parent)

		self.setWindowTitle("Filter/Sort")
		self.setWindowFlags(self.windowFlags() & Qt.WindowCloseButtonHint)
		self.resize(400, 400)
		self.setMinimumWidth(150)

		mainArea = QScrollArea(self)
		mainArea.setWidgetResizable(True)

		widget = QWidget(mainArea)
		# widget.setMinimumWidth(self.minimumWidth())

		self.flowLayout = FlowLayout(widget)
		# self.LoadTags()
		for i in range(5):
			self._addTag(f'string#{i}')

		mainArea.setWidget(widget)
		self.setWidget(mainArea)

		# self.setContextMenuPolicy(Qt.ActionsContextMenu)
	
	def LoadTags(self):
		pass
	def SaveTags(self):
		pass
	
	def _addTag(self, tag: str):
		tagWidget: QLabel = QLabel(tag)
		self.flowLayout.addWidget(tagWidget)