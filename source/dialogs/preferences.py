import os, json, typing
from PyQt5.QtCore import QModelIndex, QObject, Qt, QUrl, QAbstractItemModel, QFileInfo, QSettings
from PyQt5.QtGui import QFont, QDesktopServices, QIntValidator, QDragEnterEvent, QDropEvent, QKeySequence
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
	QSizePolicy,
	QGroupBox,
	QShortcut,
	QMessageBox
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
		self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint) # | Qt.WindowStaysOnTopHint) # https://pythonprogramminglanguage.com/pyqt5-window-flags/
		self.resize(400, 400)

		self._initUI()

		self.preferencesLoaded: bool = self.LoadPreferences()
	
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
		# self.contentStack.setCurrentIndex(1)
		
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

	def LoadPreferences(self) -> bool:
		# TODO: Use QSettings instead
		# https://gist.github.com/eyllanesc/be8a476bb7038c7579c58609d7d0f031
		# https://docs.huihoo.com/pyqt/PyQt5/pyqt_qsettings.html
		prefsFilePath: str = PreferencesWindow.GetPreferencesSavePath()
		if not os.path.isfile(prefsFilePath):
			return False

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
		return True

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
		cbRunOnStartup: QCheckBox = QCheckBox('&Run on Windows startup', self)
		cbHideOnClose: QCheckBox = QCheckBox('&Hide on close', self)
		
		# Search depth slider
		searchPathsDepthSlider: QSlider = QSlider(Qt.Horizontal)
		searchPathsDepthSlider.setMinimum(1)
		searchPathsDepthSlider.setMaximum(10)
		searchPathsDepthSlider.setSingleStep(1)
		searchPathsDepthSlider.setValue(3)
		searchPathsDepthSlider.setTickPosition(QSlider.TicksBelow)
		searchPathsDepthSlider.setTickInterval(1)
		searchPathsDepthSlider.setDisabled(True)

		layout: QFormLayout = QFormLayout()
		layout.addWidget(cbRunOnStartup)
		layout.addWidget(cbHideOnClose)
		layout.addRow(QLabel('Search depth'), searchPathsDepthSlider)
		# layout.addStretch()

		prefEntriesWidget = QWidget()
		prefEntriesWidget.setLayout(layout)

		return prefEntriesWidget

	def _createPrefAppearance(self):
		### Group 'Application'
		groupApplication: QGroupBox = QGroupBox('Application')

		grpApplicationLayout: QFormLayout = QFormLayout()
		groupApplication.setLayout(grpApplicationLayout)

		# GUI size slider
		guiSizeSLider: QSlider = QSlider(Qt.Horizontal)
		guiSizeSLider.setMinimum(1)
		guiSizeSLider.setMaximum(3)
		guiSizeSLider.setSingleStep(1)
		guiSizeSLider.setValue(2)
		guiSizeSLider.setTickPosition(QSlider.TicksBelow)
		guiSizeSLider.setTickInterval(1)
		# guiSizeSLider.setMaximumWidth(128)
		guiSizeSLider.setDisabled(True)
		grpApplicationLayout.addRow(QLabel('GUI size'), guiSizeSLider)

		### Group 'Cinema 4D Tiles'
		groupTiles: QGroupBox = QGroupBox('Cinema 4D')

		grpTilesLayout: QFormLayout = QFormLayout()
		groupTiles.setLayout(grpTilesLayout)
		
		cbC4DIcon: QCheckBox = QCheckBox('Show C4D icon')
		cbC4DIconRonalds: QCheckBox = QCheckBox('Use Ronald\'s icon set')

		def ronaldsEnabledHandler(evt):
			isChecked: bool = cbC4DIcon.isChecked()
			cbC4DIconRonalds.setEnabled(isChecked)
			if not isChecked:
				cbC4DIconRonalds.setChecked(False)
		cbC4DIcon.stateChanged.connect(ronaldsEnabledHandler)
		
		grpTilesLayout.addRow(cbC4DIcon)
		grpTilesLayout.addRow(cbC4DIconRonalds)
		grpTilesLayout.addRow(QCheckBox('Trim C4D version from folder name'))
		grpTilesLayout.addRow(QCheckBox('Show timestamp'))
		grpTilesLayout.addRow(QCheckBox('Unused folded group'))

		##### Main layout
		mainLayout: QVBoxLayout = QVBoxLayout()
		mainLayout.addWidget(groupApplication)
		mainLayout.addWidget(groupTiles)
		mainLayout.addStretch()

		main = QWidget()
		main.setLayout(mainLayout)

		return main

	def _createCustomization(self):
		prefEntriesLayout = QVBoxLayout()
		prefEntriesLayout.addWidget(QLabel("Customization"))
		prefEntriesLayout.addWidget(QLabel("TODO: Customization preferences, e.g. context menu entries with different set of g_ arguments"))
		prefEntriesLayout.addStretch()

		prefEntriesWidget = QWidget()
		prefEntriesWidget.setLayout(prefEntriesLayout)

		return prefEntriesWidget

	def _createPrefPaths(self):
		# TODO: please refactor this mess! Should be abstracted away into a separate 'SearchPathsListWidget' class to keep mess outside!
		self.pathsList.setDragDropMode(QAbstractItemView.InternalMove)

		def _addSearchPath(path: str):
			if not path or not os.path.isdir(path):
				return
			self._addSearchPath(path)
			updateButtonsEnabled()
			
		### A very ugly workaround to make it work with both d&d of items + d&d folders
		dee = self.pathsList.dragEnterEvent
		de = self.pathsList.dropEvent
		self.pathsList.setAcceptDrops(True)
		def searchPathsDragEnterEvent(evt: QDragEnterEvent):
			if evt.mimeData().hasUrls():
				evt.accept()
			dee(evt)
		def searchPathsDropEvent(evt: QDropEvent):
			if evt.mimeData().hasUrls():
				for url in evt.mimeData().urls():
					_addSearchPath(url.toLocalFile())
				evt.accept()
			de(evt)
		self.pathsList.dragEnterEvent = searchPathsDragEnterEvent
		self.pathsList.dropEvent = searchPathsDropEvent

		buttons = {
			'add': QPushButton('Add path'),
			'remove': QPushButton('Remove'),
		}
		def updateButtonsEnabled():
			buttons['remove'].setEnabled(self.pathsList.currentRow() >= 0)
		updateButtonsEnabled()

		def _deleteSelectedRow():
			if self.pathsList.currentRow() < 0:
				return
			self.pathsList.takeItem(self.pathsList.currentRow())
			updateButtonsEnabled()

		delShortcut: QShortcut = QShortcut(QKeySequence(Qt.Key_Delete), self.pathsList)
		delShortcut.activated.connect(_deleteSelectedRow)


		self.pathsList.itemSelectionChanged.connect(lambda: updateButtonsEnabled())
		self.pathsList.doubleClicked.connect(lambda: OpenFolderInDefaultExplorer(self.pathsList.currentItem().text()))

		def btnAddClicked(evt):
			filePath: str = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
			_addSearchPath(filePath)

		buttons['add'].clicked.connect(btnAddClicked)
		buttons['remove'].clicked.connect(lambda evt: _deleteSelectedRow())
		
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
