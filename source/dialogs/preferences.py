import os, json
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont, QDesktopServices
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
	QFileDialog,
	QLayout
)

from version import *
import utils

class PreferencesWindow(QMainWindow):
	PREFERENCES_FILENAME = 'preferences.json'

	def __init__(self, parent=None):
		super().__init__(parent)

		self.pathsList = QListWidget()

		self.LoadPreferences()

		self.categories = {
			'General': self._createPrefGeneral(),
			'Appearance': self._createPrefAppearance(),
			'Search paths': self._createPrefPaths()
		}

		self.setWindowTitle("Preferences")
		self.setWindowFlags(self.windowFlags() & Qt.WindowCloseButtonHint)
		self.resize(400, 200)

		# Stack of widgets containing preferences per category
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

		# Preferences buttons
		self.openPreferencesFolderButton: QPushButton = QPushButton('Open preferences folder')
		self.openPreferencesFolderButton.clicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(utils.GetPrefsFolderPath())))
		self.savePreferencesButton: QPushButton = QPushButton('Save preferences')
		self.savePreferencesButton.clicked.connect(self.SavePreferences)
		# Save preferences layout
		self.savePreferencesLayout: QHBoxLayout = QHBoxLayout()
		self.savePreferencesLayout.addWidget(self.openPreferencesFolderButton)
		self.savePreferencesLayout.addStretch()
		self.savePreferencesLayout.addWidget(self.savePreferencesButton)
		savePreferencesWidget: QWidget = QWidget()
		savePreferencesWidget.setLayout(self.savePreferencesLayout)

		# Intermediate layout to separate preferences entries widget from save-prefs button
		self.contentLayout: QVBoxLayout = QVBoxLayout()
		self.contentLayout.addWidget(self.contentStack)
		self.contentLayout.addWidget(savePreferencesWidget)
		contentWidget: QWidget = QWidget()
		contentWidget.setLayout(self.contentLayout)

		# Main layout of prefs window
		self.prefsLayout: QHBoxLayout = QHBoxLayout()
		self.prefsLayout.addWidget(self.categoriesWidget)
		self.prefsLayout.addWidget(contentWidget)

		centralWidget = QWidget()
		centralWidget.setLayout(self.prefsLayout)
		self.setCentralWidget(centralWidget)
	
	def GetSearchPaths(self):
		return [self.pathsList.item(i).text() for i in range(self.pathsList.count())]

	@staticmethod
	def GetPreferencesSavePath():
		prefsFolderPath: str = utils.GetPrefsFolderPath()
		return os.path.join(prefsFolderPath, PreferencesWindow.PREFERENCES_FILENAME)

	def LoadPreferences(self):
		prefsFilePath: str = PreferencesWindow.GetPreferencesSavePath()
		if not os.path.isfile(prefsFilePath):
			return

		with open(prefsFilePath, 'r') as fp:
			data: dict = json.load(fp)
			if 'version' in data:
				print(f"C4D Version Manager: v{data['version']}")
			if 'preferences' in data:
				prefs: dict = data['preferences']
				if 'search_paths' in prefs:
					sPaths: list[str] = prefs['search_paths']
					self.pathsList.clear()
					for p in sPaths:
						self._addSearchPath(p)

	def SavePreferences(self):
		storeDict: dict = dict()
		storeDict['version'] = C4DL_VERSION
		storeDict['preferences'] = dict()

		prefsDict: dict = storeDict['preferences']
		prefsDict['search_paths'] = list()
		for p in self.GetSearchPaths():
			prefsDict['search_paths'].append(p)

		prefsFilePath: str = PreferencesWindow.GetPreferencesSavePath()
		with open(prefsFilePath, 'w') as fp:
			json.dump(storeDict, fp)


	def _addSearchPath(self, path: str):
		newItem = QListWidgetItem(path)
		self.pathsList.addItem(newItem)
		self.pathsList.setCurrentItem(newItem)
	
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
		# for p in self.searchPaths:
		# 	self._addSearchPath(p)

		buttons = {
			'add': QPushButton('+'),
			'remove': QPushButton('-'),
			'up': QPushButton('↑'),
			'down': QPushButton('↓'),
		}
		def updateButtonsEnabled():
			curRow = self.pathsList.currentRow()
			somethingSelected = curRow >= 0
			buttons['remove'].setEnabled(somethingSelected)
			buttons['up'].setEnabled(somethingSelected and curRow > 0)
			buttons['down'].setEnabled(somethingSelected and curRow < self.pathsList.count() - 1)

		self.pathsList.doubleClicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(self.pathsList.currentItem().text())))
		
		for btn in buttons.values():
			btn.setFont(QFont('Comic Sans MS', 11))
			btn.setFixedWidth(32)

		def btnAddClicked(t):
			filePath: str = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
			# print('btnAdd: ', filePath)
			self._addSearchPath(filePath)
			updateButtonsEnabled()
		buttons['add'].clicked.connect(btnAddClicked)

		def btnRemoveClicked(t):
			# print('btnRemove: ', t)
			if self.pathsList.currentRow() < 0:
				return
			self.pathsList.takeItem(self.pathsList.currentRow())
			updateButtonsEnabled()
		buttons['remove'].clicked.connect(btnRemoveClicked)
		
		buttonsLayout = QHBoxLayout()
		for btn in buttons.values():
			buttonsLayout.addWidget(btn)
		buttonsLayout.addStretch()

		buttonsGroupWidget = QWidget()
		buttonsGroupWidget.setLayout(buttonsLayout)

		layout = QVBoxLayout()
		layout.addWidget(self.pathsList)
		layout.addWidget(buttonsGroupWidget)

		prefEntriesWidget = QWidget()
		prefEntriesWidget.setLayout(layout)

		return prefEntriesWidget
