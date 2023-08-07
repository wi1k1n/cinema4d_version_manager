import os, json
from functools import partial
from typing import Any

from PyQt5.QtCore import (
    QModelIndex, QObject, Qt, QUrl, QAbstractItemModel, QFileInfo, QSettings, pyqtSignal
)
from PyQt5.QtGui import (
    QFont, QDesktopServices, QIntValidator, QDragEnterEvent, QDropEvent, QKeySequence
)
from PyQt5.QtWidgets import (
	QLabel, QMainWindow, QDialog, QHBoxLayout, QListWidget, QWidget, QVBoxLayout, QPushButton,
	QListWidgetItem, QStackedWidget, QFileDialog, QLayout, QAbstractItemView, QFormLayout,
	QCheckBox, QSlider, QSizePolicy, QGroupBox, QShortcut, QMessageBox, QComboBox, QLineEdit
)

from version import *
from utils import *

class StorablePreference:
	def __init__(self, getter, setter, default = None) -> None:
		self.getter = getter
		self.setter = setter
		self.default = default
	
	def Get(self):
		return self.getter()
	def Set(self, val):
		if val is not None:
			return self.setter(val)
		return False
	def Reset(self):
		return self.Set(self.default)

class PreferencesWindow(QMainWindow):
	PREFERENCES_FILENAME = 'preferences.json'

	preferenceChangedSignal = pyqtSignal(str) # key of changed preference

	def __init__(self, parent=None):
		super().__init__(parent)

		self.storablePrefs: dict[str, StorablePreference] = dict()

		self.setWindowTitle("Preferences")
		self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint) # | Qt.WindowStaysOnTopHint) # https://pythonprogramminglanguage.com/pyqt5-window-flags/
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
		self.openPreferencesFolderButton.clicked.connect(lambda: OpenFolderInDefaultExplorer(GetPrefsFolderPath()))
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

	def GetPreference(self, attr: str) -> ...:
		if attr not in self.storablePrefs:
			return None
		return self.storablePrefs[attr].Get()

	def IsPreferencesLoaded(self) -> bool:
		return hasattr(self, 'preferencesLoaded') and self.preferencesLoaded
	
	def _connectPreference(self, attr: str, getter, setter, default = None, onChangeSignal: pyqtSignal | None = None) -> bool:
		self.storablePrefs[attr] = StorablePreference(getter, setter, default)
		if onChangeSignal:
			onChangeSignal.connect(lambda: self.preferenceChangedSignal.emit(attr))
		return True
	
	def _connectPreferenceSimple(self, attr: str, obj, default = None, onChangeSignal: pyqtSignal | None = None) -> bool:
		if isinstance(obj, QCheckBox): return self._connectPreference(attr, obj.isChecked, obj.setChecked, default, obj.stateChanged)
		if isinstance(obj, QSlider): return self._connectPreference(attr, obj.value, obj.setValue, default, obj.valueChanged)
		if isinstance(obj, QComboBox): return self._connectPreference(attr, obj.currentIndex, obj.setCurrentIndex, default, obj.currentIndexChanged)
		if isinstance(obj, QLineEdit): return self._connectPreference(attr, obj.text, obj.setText, default, obj.textChanged)
		return False
	
	def _setPreference(self, attr: str, val):
		if attr in self.storablePrefs:
			self.storablePrefs[attr].Set(val)

	def LoadPreferences(self) -> bool:
		# TODO: Use QSettings instead
		# https://gist.github.com/eyllanesc/be8a476bb7038c7579c58609d7d0f031
		# https://docs.huihoo.com/pyqt/PyQt5/pyqt_qsettings.html
		prefsFilePath: str = PreferencesWindow.GetPreferencesSavePath()
		if not os.path.isfile(prefsFilePath):
			# Set defaults
			for pref in self.storablePrefs.values():
				pref.Reset()
			return False

		with open(prefsFilePath, 'r') as fp:
			data: dict = json.load(fp)
			if 'version' in data:
				print(f"Loading preferences: file version {data['version']}")
			if 'preferences' in data:
				prefs: dict = data['preferences']
				for attr, pref in self.storablePrefs.items():
					if attr in prefs:
						pref.Set(prefs[attr])
		self.preferencesLoaded = True
		return True

	def SavePreferences(self):
		storeDict: dict = dict()
		storeDict['version'] = C4DL_VERSION
		storeDict['preferences'] = dict() # pref attributes from preferences window

		for attr, pref in self.storablePrefs.items():
			storeDict['preferences'][attr] = pref.Get()

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
		SECTION_PREFIX = 'general_'

		# # TODO: disabled until filter / sort / search isn't implemented
		# # Search depth slider
		# searchPathsDepthSlider: QSlider = QSlider(Qt.Horizontal)
		# searchPathsDepthSlider.setMinimum(1)
		# searchPathsDepthSlider.setMaximum(5)
		# searchPathsDepthSlider.setSingleStep(1)
		# # searchPathsDepthSlider.setValue(2)
		# searchPathsDepthSlider.setTickPosition(QSlider.TicksBelow)
		# searchPathsDepthSlider.setTickInterval(1)
		# searchPathsDepthSlider.setDisabled(True)
		# self._connectPreferenceSimple(f'{SECTION_PREFIX}search-depth', searchPathsDepthSlider, 2)
		# layout.addRow(QLabel('Search depth'), searchPathsDepthSlider)
		
		# System
		cbRunOnStartup: QPushButton = QPushButton('&Set up run on startup', self)
		cbRunOnStartup.clicked.connect(self._setRunOnStartup)
		cbHideOnClose: QCheckBox = QCheckBox('&Hide on close', self)
		self._connectPreferenceSimple(f'{SECTION_PREFIX}hide-on-close', cbHideOnClose, False)
		
		systemLayout: QFormLayout = QFormLayout()
		systemLayout.addWidget(cbHideOnClose)
		systemLayout.addWidget(cbRunOnStartup)

		grpbSystem: QGroupBox = QGroupBox('System', self)
		grpbSystem.setLayout(systemLayout)

		# # Keyboard
		# keyboardLayout: QFormLayout = QFormLayout()
		# leGlobalShortcut: QLineEdit = QLineEdit()
		# leGlobalShortcut.setReadOnly(True)
		
		# systemLayout: QFormLayout = QFormLayout()
		# grpbKeyboard: QGroupBox = QGroupBox('Keyboard', self)
		# grpbKeyboard.setLayout(systemLayout)

		# Main General preferences
		prefEntriesLayout: QVBoxLayout = QVBoxLayout()
		prefEntriesLayout.addWidget(grpbSystem)
		prefEntriesLayout.addStretch()

		prefEntriesWidget = QWidget()
		prefEntriesWidget.setLayout(prefEntriesLayout)
		return prefEntriesWidget

	def _createPrefAppearance(self):
		SECTION_PREFIX = 'appearance_'
		# ### Group 'Application'
		# groupApplication: QGroupBox = QGroupBox('Application')

		# grpApplicationLayout: QFormLayout = QFormLayout()
		# groupApplication.setLayout(grpApplicationLayout)

		# # GUI size slider
		# guiSizeSLider: QSlider = QSlider(Qt.Horizontal)
		# guiSizeSLider.setMinimum(1)
		# guiSizeSLider.setMaximum(3)
		# guiSizeSLider.setSingleStep(1)
		# # guiSizeSLider.setValue(2)
		# guiSizeSLider.setTickPosition(QSlider.TicksBelow)
		# guiSizeSLider.setTickInterval(1)
		# self._connectPreferenceSimple(f'{SECTION_PREFIX}gui-scale', guiSizeSLider, 2)
		# # guiSizeSLider.setMaximumWidth(128)
		# guiSizeSLider.setDisabled(True)
		# grpApplicationLayout.addRow(QLabel('GUI size'), guiSizeSLider)

		### Group 'Cinema 4D Tiles'
		groupTiles: QGroupBox = QGroupBox('Cinema 4D Tiles')

		grpTilesLayout: QFormLayout = QFormLayout()
		groupTiles.setLayout(grpTilesLayout)
		
		cbC4DIconRonalds: QCheckBox = QCheckBox('Use Ronald\'s icon set')
		self._connectPreferenceSimple(f'{SECTION_PREFIX}ronalds-icons', cbC4DIconRonalds, True)

		cbAdjustC4DFolderName: QCheckBox = QCheckBox('Adjust C4D folder name')
		self._connectPreferenceSimple(f'{SECTION_PREFIX}c4dtile-adjust-c4d-folder-name', cbAdjustC4DFolderName, True)

		cbShowTimestamp: QCheckBox = QCheckBox('Show timestamp')
		self._connectPreferenceSimple(f'{SECTION_PREFIX}c4dtile-show-timestamp', cbShowTimestamp, True)
		cbTimestampFormat: QLineEdit = QLineEdit('%d-%b-%Y %H:%M')
		self._connectPreferenceSimple(f'{SECTION_PREFIX}c4dtile-timestamp-format', cbTimestampFormat)
		PreferencesWindow._connectWidgetsIsEnabledToCheckbox(cbShowTimestamp, [cbTimestampFormat])
		def showInvalidTimeFormat(le: QLineEdit):
			clr: str = '#ffffff'
			try:
				dt.datetime.now().strftime(le.text())
			except:
				clr = '#ffa7a7'
			le.setStyleSheet(f'background-color: {clr}')
		cbTimestampFormat.textChanged.connect(partial(showInvalidTimeFormat, cbTimestampFormat))

		cbShoNoteOnTile: QCheckBox = QCheckBox('Show note on tile')
		self._connectPreferenceSimple(f'{SECTION_PREFIX}c4dtile-show-note', cbShoNoteOnTile, True)
		cbShowNoteOnTileFirstLineOnly: QCheckBox = QCheckBox('Show note: only show first line')
		self._connectPreferenceSimple(f'{SECTION_PREFIX}c4dtile-show-note-first-line', cbShowNoteOnTileFirstLineOnly, True)
		PreferencesWindow._connectWidgetsIsEnabledToCheckbox(cbShoNoteOnTile, [cbShowNoteOnTileFirstLineOnly])
		
		cbUnusedFolderGroup: QCheckBox = QCheckBox('Unused folded group')
		self._connectPreferenceSimple(f'{SECTION_PREFIX}unused-folded-group', cbUnusedFolderGroup)

		grpTilesLayout.addRow(cbC4DIconRonalds)
		grpTilesLayout.addRow(cbAdjustC4DFolderName)
		grpTilesLayout.addRow(cbShowTimestamp)
		grpTilesLayout.addRow('Timestamp format', cbTimestampFormat)
		grpTilesLayout.addRow(cbUnusedFolderGroup)
		grpTilesLayout.addRow(cbShoNoteOnTile)
		grpTilesLayout.addRow(cbShowNoteOnTileFirstLineOnly)
		
		comboC4DStatusGrouping: QComboBox = QComboBox(self)
		comboC4DStatusGrouping.addItems(['Touched / Untouched', 'Separate statuses'])
		def comboC4DStatusGroupingGetter(cb: QComboBox):
			return cb.currentIndex()
		def comboC4DStatusGroupingSetter(cb: QComboBox, val: int):
			cb.setCurrentIndex(val)
		self._connectPreference(f'{SECTION_PREFIX}grouping-status-separately',
			  partial(comboC4DStatusGroupingGetter, comboC4DStatusGrouping),
			  partial(comboC4DStatusGroupingSetter, comboC4DStatusGrouping), 0,
			  comboC4DStatusGrouping.currentIndexChanged)

		grpTilesLayout.addRow(QLabel('C4D "Grouping by status" mode:'), comboC4DStatusGrouping)

		##### Main layout
		mainLayout: QVBoxLayout = QVBoxLayout()
		mainLayout.addWidget(groupTiles)
		mainLayout.addStretch()

		main = QWidget()
		main.setLayout(mainLayout)

		return main

	def _createCustomization(self):
		SECTION_PREFIX = 'customization_'
		prefEntriesLayout = QVBoxLayout()
		prefEntriesLayout.addWidget(QLabel("Customization"))
		prefEntriesLayout.addWidget(QLabel(f"TODO: Customization preferences,{os.linesep}e.g. context menu entries with different set of g_ arguments"))
		prefEntriesLayout.addStretch()

		prefEntriesWidget = QWidget()
		prefEntriesWidget.setLayout(prefEntriesLayout)

		return prefEntriesWidget

	def _createPrefPaths(self):
		# TODO: please refactor this mess! Should be abstracted away into a separate 'SearchPathsListWidget' class to keep mess outside!
		SECTION_PREFIX = 'search-paths_'
		def prefConnectPathListGetter():
			return [self.pathsList.item(i).text() for i in range(self.pathsList.count())]
		def prefConnectPathListSetter(val: list[str]):
			self.pathsList.clear()
			for v in val:
				self._addSearchPath(v)
		self._connectPreference(f'{SECTION_PREFIX}search-paths', prefConnectPathListGetter, prefConnectPathListSetter, [])

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
	
	def _setRunOnStartup(self, val: int):
		if startupPath := GetStartupPath():
			if QMessageBox.information(self, 'Instructions', 'Two folders will be opened for you.'\
				'\nCopy executable file (Ctrl+C) from the first one, and paste a shortcut'\
				' (Right Mouse Button -> Paste shortcut) in the second on. Do you want to continue?',
				QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
				ShowFileInDefaultExplorer(GetCurrentExecutablePath())
				OpenFolderInDefaultExplorer(startupPath)
			# CreateSymlink(executablePath, os.path.join(startupPath, os.path.split(executablePath)[1])) # not enough access rights!
	
	@staticmethod
	def _connectWidgetsIsEnabledToCheckbox(cb: QCheckBox, widgets: list[QWidget]):
		def SetEnabled(wList: list[QWidget], val: bool):
			for w in wList:
				w.setEnabled(val)
		cb.stateChanged.connect(partial(SetEnabled, widgets))

	@staticmethod
	def GetPreferencesSavePath():
		prefsFolderPath: str = GetPrefsFolderPath()
		return os.path.join(prefsFolderPath, PreferencesWindow.PREFERENCES_FILENAME)
