from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
	QLabel,
	QMainWindow,
	QDialog,
	QHBoxLayout,
	QListWidget,
	QWidget,
	QVBoxLayout,
	QPushButton,
	QListWidgetItem,
	QStackedWidget,
	QFileDialog
)

class PreferencesWindow(QMainWindow):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.categories = {
			'General': self._createPrefGeneral(),
			'Appearance': self._createPrefAppearance(),
			'Search paths': self._createPrefPaths()
		}

		self.setWindowTitle("Preferences")
		self.setWindowFlags(self.windowFlags() & Qt.WindowCloseButtonHint)
		self.resize(400, 200)
		
		# Stack of widgets containing pref entries for each category
		self.contentStack = QStackedWidget()
		for v in self.categories.values():
			if v is not None:
				self.contentStack.addWidget(v)
		self.contentStack.setCurrentIndex(0)
		
		# List with preferences categories
		self.categoriesWidget = QListWidget()
		self.categoriesWidget.setMinimumWidth(150)
		self.categoriesWidget.setMinimumHeight(50)
		for k in self.categories.keys():
			self.categoriesWidget.addItem(k)
		self.categoriesWidget.setFixedWidth(self.categoriesWidget.sizeHintForColumn(0) + 2 * self.categoriesWidget.frameWidth() + 10)
		self.categoriesWidget.currentItemChanged.connect(self._prefCategoryChanged)
		self.categoriesWidget.setCurrentRow(0)
		

		# Main layout of prefs window
		self.prefsLayout: QHBoxLayout = QHBoxLayout()
		self.prefsLayout.addWidget(self.categoriesWidget)
		self.prefsLayout.addWidget(self.contentStack)

		self.centralWidget = QWidget()
		self.centralWidget.setLayout(self.prefsLayout)
		self.setCentralWidget(self.centralWidget)
	
	def GetSearchPaths(self):
		return ['D:\\Downloads']
	
	def _prefCategoryChanged(self, cur: QListWidgetItem, prev):
		if cur is None:
			return
		self.contentStack.setCurrentIndex(self.categoriesWidget.currentRow())

	def _createPrefGeneral(self):
		prefEntriesLayout = QVBoxLayout()
		prefEntriesLayout.addWidget(QLabel("Hello, World"))
		prefEntriesLayout.addWidget(QLabel("Hello, PyQt!"))
		prefEntriesLayout.addWidget(QPushButton("Button"))
		prefEntriesLayout.addStretch()

		prefEntriesWidget = QWidget()
		prefEntriesWidget.setLayout(prefEntriesLayout)

		return prefEntriesWidget

	def _createPrefAppearance(self):
		prefEntriesLayout = QVBoxLayout()
		prefEntriesLayout.addWidget(QLabel("Appearance"))
		prefEntriesLayout.addStretch()

		prefEntriesWidget = QWidget()
		prefEntriesWidget.setLayout(prefEntriesLayout)

		return prefEntriesWidget

	def _createPrefPaths(self):
		pathsList = QListWidget()
		buttons = {
			'add': QPushButton('+'),
			'remove': QPushButton('-'),
			'up': QPushButton('↑'),
			'down': QPushButton('↓'),
		}
		def updateButtonsEnabled():
			curRow = pathsList.currentRow()
			somethingSelected = curRow >= 0
			buttons['remove'].setEnabled(somethingSelected)
			buttons['up'].setEnabled(somethingSelected and curRow > 0)
			buttons['down'].setEnabled(somethingSelected and curRow < pathsList.count() - 1)
			
		# for idx in range(pathsList.count()):
		# 	item = pathsList.item(idx)
		# 	item.setFlags(item.flags() | Qt.ItemIsEditable)

		def pathListClicked(cur):
			print(cur)
			updateButtonsEnabled()
		pathsList.clicked.connect(pathListClicked)
		
		for btn in buttons.values():
			btn.setFont(QFont('Comic Sans MS', 11))
			btn.setFixedWidth(32)


		def btnAddClicked(t):
			filePath: str = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
			newItem = QListWidgetItem(filePath)
			pathsList.addItem(newItem)
			pathsList.setCurrentItem(newItem)
			print('btnAdd: ', filePath)
			updateButtonsEnabled()
		buttons['add'].clicked.connect(btnAddClicked)

		def btnRemoveClicked(t):
			print('btnRemove: ', t)
			updateButtonsEnabled()
		buttons['remove'].clicked.connect(btnRemoveClicked)
		
		buttonsLayout = QHBoxLayout()
		buttonsLayout.addStretch()
		for btn in buttons.values():
			buttonsLayout.addWidget(btn)

		buttonsGroupWidget = QWidget()
		buttonsGroupWidget.setLayout(buttonsLayout)

		layout = QVBoxLayout()
		layout.addWidget(pathsList)
		# layout.addWidget(QLabel("Path2"))
		layout.addWidget(buttonsGroupWidget)
		# layout.addStretch()

		prefEntriesWidget = QWidget()
		prefEntriesWidget.setLayout(layout)

		return prefEntriesWidget
