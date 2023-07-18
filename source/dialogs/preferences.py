import sys
from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (
	QApplication, QLabel, QMainWindow, QMenu, QMenuBar, QToolBar, QAction, QSpinBox, QHBoxLayout, QListWidget, QWidget, QVBoxLayout, QPushButton
)

class PreferencesWindow(QMainWindow):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.categories = {
			'General': self._createPrefGeneral(),
			'Search paths': None
		}

		self.setWindowTitle("Preferences")
		self.resize(400, 300)
		
		prefCategoriesWidget = QListWidget()
		prefCategoriesWidget.setMinimumWidth(100)
		for k in self.categories.keys():
			prefCategoriesWidget.addItem(k)
		prefCategoriesWidget.setFixedSize(prefCategoriesWidget.sizeHintForColumn(0) + 2 * prefCategoriesWidget.frameWidth() + 4, prefCategoriesWidget.height())
		
		layout = QHBoxLayout()
		layout.addWidget(prefCategoriesWidget)
		layout.addWidget(next(iter(self.categories.values())))

		self.centralWidget = QWidget()
		self.centralWidget.setLayout(layout)
		self.setCentralWidget(self.centralWidget)
	
	def _createPrefGeneral(self):
		prefEntriesLayout = QVBoxLayout()
		prefEntriesLayout.addWidget(QLabel("Hello, World"))
		prefEntriesLayout.addWidget(QLabel("Hello, PyQt!"))
		prefEntriesLayout.addWidget(QPushButton("Button"))
		prefEntriesLayout.addStretch()

		prefEntriesWidget = QWidget()
		prefEntriesWidget.setLayout(prefEntriesLayout)

		return prefEntriesWidget
