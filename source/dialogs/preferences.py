import os, json, typing
from PyQt5.QtCore import QModelIndex, QObject, Qt, QUrl, QAbstractItemModel, QFileInfo, QSettings
from PyQt5.QtGui import QFont, QDesktopServices, QIntValidator
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
	QLayout,
	QAbstractItemView,
	QFormLayout,
	QCheckBox,
	QSlider,
	QSizePolicy
)

from version import *
import utils
from utils import OpenFolderInDefaultExplorer

class PreferencesEntries(int):
	SearchPaths: int = ...

class PreferencesWindow(QMainWindow):
	PREFERENCES_FILENAME = 'preferences.json'

	def __init__(self, parent=None):
		super().__init__(parent)

		self.setWindowTitle("Preferences")
		self.setWindowFlags(self.windowFlags() & Qt.WindowCloseButtonHint)
		self.resize(400, 400)

		self._initUI()

		self.LoadPreferences()
	
	def _initUI(self):
		self.pathsList = QListWidget()
		self.categories = {
			'General': self._createPrefGeneral(),
			'Appearance': self._createPrefAppearance(),
			'Search paths': self._createPrefPaths(),
			'Customization': self._createCustomization(),
		}

		# Stack of widgets containing preferences per category
		self.contentStack = QStackedWidget()
		for v in self.categories.values():
			if v is not None:
				self.contentStack.addWidget(v)
		self.contentStack.setCurrentIndex(0)
		
		# List with preferences categories
		self.categoriesWidget = QListWidget()
		self.categoriesWidget.setMinimumHeight(100)
		for k in self.categories.keys():
			self.categoriesWidget.addItem(k)
		self.categoriesWidget.currentItemChanged.connect(self._prefCategoryChanged)
		self.categoriesWidget.setCurrentRow(0)

		# Preferences buttons
		self.openPreferencesFolderButton: QPushButton = QPushButton('Open prefs folder')
		self.openPreferencesFolderButton.clicked.connect(lambda: OpenFolderInDefaultExplorer(utils.GetPrefsFolderPath()))
		self.savePreferencesButton: QPushButton = QPushButton('Save preferences')
		self.savePreferencesButton.clicked.connect(self.SavePreferences)

		# Intermediate layout to separate preferences entries widget from save-prefs button
		self.contentLayout: QVBoxLayout = QVBoxLayout()
		self.contentLayout.addWidget(self.categoriesWidget)
		self.contentLayout.addWidget(self.openPreferencesFolderButton)
		self.contentLayout.addWidget(self.savePreferencesButton)
		contentWidget: QWidget = QWidget()
		contentWidget.setLayout(self.contentLayout)
		contentWidget.setFixedWidth(contentWidget.minimumSizeHint().width())

		# Main layout of prefs window
		self.prefsLayout: QHBoxLayout = QHBoxLayout()
		self.prefsLayout.addWidget(contentWidget)
		self.prefsLayout.addWidget(self.contentStack)

		centralWidget = QWidget()
		centralWidget.setLayout(self.prefsLayout)
		centralWidget.setMinimumWidth(self.width())
		self.setCentralWidget(centralWidget)

	def GetPreference(self, attr: PreferencesEntries) -> ...:
		if attr == PreferencesEntries.SearchPaths:
			return [self.pathsList.item(i).text() for i in range(self.pathsList.count())]

	def LoadPreferences(self):
		# TODO: Use QSettings instead
		# https://gist.github.com/eyllanesc/be8a476bb7038c7579c58609d7d0f031
		# https://docs.huihoo.com/pyqt/PyQt5/pyqt_qsettings.html
		prefsFilePath: str = PreferencesWindow.GetPreferencesSavePath()
		if not os.path.isfile(prefsFilePath):
			return

		with open(prefsFilePath, 'r') as fp:
			data: dict = json.load(fp)
			if 'version' in data:
				print(f"Loading preferences: file version {data['version']}")
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
		storeDict['preferences'] = dict() # pref attributes from preferences window

		# Preferences
		prefsDict: dict = storeDict['preferences']
		prefsDict['search_paths'] = list()
		for p in self.GetPreference(PreferencesEntries.SearchPaths):
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
		cbHideOnClose: QCheckBox = QCheckBox('&Hide on close', self)

		layout: QFormLayout = QFormLayout()
		layout.addWidget(cbHideOnClose)
		# layout.addStretch()

		prefEntriesWidget = QWidget()
		prefEntriesWidget.setLayout(layout)

		return prefEntriesWidget

	def _createPrefAppearance(self):
		guiSizeSLider: QSlider = QSlider(Qt.Horizontal)
		guiSizeSLider.setMinimum(1)
		guiSizeSLider.setMaximum(3)
		guiSizeSLider.setSingleStep(1)
		guiSizeSLider.setValue(2)
		guiSizeSLider.setTickPosition(QSlider.TicksBelow)
		guiSizeSLider.setTickInterval(1)
		# guiSizeSLider.setMaximumWidth(128)
		guiSizeSLider.setDisabled(True)

		layout: QFormLayout = QFormLayout()
		layout.addRow(QLabel('GUI size'), guiSizeSLider)

		prefEntriesWidget = QWidget()
		prefEntriesWidget.setLayout(layout)

		return prefEntriesWidget

	def _createCustomization(self):
		prefEntriesLayout = QVBoxLayout()
		prefEntriesLayout.addWidget(QLabel("Customization"))
		prefEntriesLayout.addWidget(QLabel("TODO: Customization preferences, e.g. context menu entries with different set of g_ arguments"))
		prefEntriesLayout.addStretch()

		prefEntriesWidget = QWidget()
		prefEntriesWidget.setLayout(prefEntriesLayout)

		return prefEntriesWidget

	def _createPrefPaths(self):
		self.pathsList.setDragDropMode(QAbstractItemView.InternalMove)

		buttons = {
			'add': QPushButton('Add path'),
			'remove': QPushButton('Remove'),
		}
		def updateButtonsEnabled():
			buttons['remove'].setEnabled(self.pathsList.currentRow() >= 0)
		updateButtonsEnabled()

		self.pathsList.itemSelectionChanged.connect(lambda: updateButtonsEnabled())
		self.pathsList.doubleClicked.connect(lambda: OpenFolderInDefaultExplorer(self.pathsList.currentItem().text()))

		def btnAddClicked(t):
			filePath: str = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
			if filePath:
				self._addSearchPath(filePath)
				updateButtonsEnabled()
		buttons['add'].clicked.connect(btnAddClicked)

		def btnRemoveClicked(t):
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

	@staticmethod
	def GetPreferencesSavePath():
		prefsFolderPath: str = utils.GetPrefsFolderPath()
		return os.path.join(prefsFolderPath, PreferencesWindow.PREFERENCES_FILENAME)
