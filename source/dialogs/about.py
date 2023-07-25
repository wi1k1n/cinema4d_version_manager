import sys
from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QKeySequence, QFont
from PyQt5.QtWidgets import (
	QApplication, QLabel, QMainWindow, QMenu, QMenuBar, QToolBar, QAction, QSpinBox, QDialog, QVBoxLayout
)

import version
from utils import *

class AboutWindow(QDialog):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle("About")
		self.setWindowFlags(self.windowFlags() & ~Qt.WindowMinimizeButtonHint | Qt.FramelessWindowHint)
		self.setFixedSize(600, 400)
		self.setStyleSheet("background-color: #c2ffe0;")

		self.centralWidget = QLabel("Cinema 4D version manager"
									+ f"\n\nVersion: {version.C4DL_VERSION}")
		self.centralWidget.setFont(QFont(APPLICATION_FONT_FAMILY, 20))
		self.centralWidget.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

		mainLayout: QVBoxLayout = QVBoxLayout()
		mainLayout.addWidget(self.centralWidget)
		self.setLayout(mainLayout)

		self.mousePressEvent = lambda evt: self.hide()
		self.keyPressEvent = lambda evt: self.hide()