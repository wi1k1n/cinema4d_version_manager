import sys, os, typing, datetime as dt
from subprocess import Popen, PIPE
from functools import partial

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QObject, Qt, QEvent, pyqtSignal, QProcess, QPoint, QRect
from PyQt5.QtGui import QIcon, QKeySequence, QPixmap, QFont, QCursor, QMouseEvent, QDropEvent, QDragEnterEvent, QKeyEvent, QCloseEvent
from PyQt5.QtWidgets import (
	QApplication,
	QLabel,
	QMainWindow,
	QMenu, QMenuBar,
	QStyle,
	QStyleHintReturn,
	QStyleOption,
	QToolBar,
	QAction,
	QWidget,
	QTabWidget,
	QLayout, QVBoxLayout, QHBoxLayout,
	QFrame,
	QScrollArea,
	QGroupBox,
	QTreeWidget, QTreeWidgetItem,
	QStatusBar,
	QProxyStyle,
	QMessageBox,
)

# import qrc_resources
from dialogs.preferences import PreferencesWindow, PreferencesEntries
from dialogs.about import AboutWindow
from dialogs.help import HelpWindow
from dialogs.tags import TagsWindow, C4DTag
from dialogs.filtersort import FilterSortWindow
from dialogs.main_window_tiles import *
from utils import *
from gui_utils import *

# TODO: here for now, please remove once not needed!
class TestMainWindow(QMainWindow):
	def __init__(self, parent: QWidget | None = None) -> None:
		super(TestMainWindow, self).__init__(parent)

		self.setWindowTitle("Test Main window")
		self.resize(800, 600)

		layout: QVBoxLayout = QVBoxLayout()
		layout.addWidget(C4DTile(C4DInfo('', [])))
		layout.addWidget(C4DTile(C4DInfo('', [])))
		layout.addWidget(QLabel('hey there'))

		widget: QWidget = QWidget()
		widget.setLayout(layout)

		self.setCentralWidget(widget)
		

		self.update()










class MainWindow(QMainWindow):
	GROUPING_MARK_ASC_PREFIX: str = '▲ '
	GROUPING_MARK_DESC_PREFIX: str = '▼ '

	"""Main Window."""
	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)

		self.setWindowTitle("C4D Version Manager")
		self.resize(1420, 840)
		self.setMinimumSize(350, 250)

		self.dialogs = {
			'preferences': PreferencesWindow(),
			'tags': TagsWindow(),
			'filtersort': FilterSortWindow(),
			'about': AboutWindow(),
			'help': HelpWindow(),
		}

		self.c4dTabTiles: C4DTilesWidget = C4DTilesWidget(self)
		self.c4dTabTiles.c4dStatusChanged.connect(lambda info, status: self.updateTilesWidget()) # update tiles if c4d status was changed

		# self.c4dTabTableWidget: QTreeWidget = QTreeWidget(self)
		# self.c4dTabTableWidget.setColumnCount(4)
		# self.c4dTabTableWidget.setHeaderLabels(['Fav', 'Path', 'Version', 'Date'])
		# for i in range(5):
		# 	item: QTreeWidgetItem = QTreeWidgetItem(self.c4dTabTableWidget)
		# 	for j in range(self.c4dTabTableWidget.columnCount()):
		# 		item.setText(j, f'Col#{i}: text{j}')

		self.centralWidget = QTabWidget()
		self.centralWidget.addTab(self.c4dTabTiles, "Tiles")
		# self.centralWidget.addTab(self.c4dTabTableWidget, "Table")
		
		self.setCentralWidget(self.centralWidget)

		self._createActions()
		self._createMenuBar()
		self._createToolBars()
		self._createContextMenu()
		self._createStatusBar()

		self.dialogs['tags'].tagEditedSignal.connect(lambda tag: self.c4dTabTiles._rebuildWidget())
		self.dialogs['tags'].tagRemovedSignal.connect(lambda tag: self.c4dTabTiles._tagRemoveFromAll(tag))
		self.dialogs['tags'].tagOrderChangedSignal.connect(lambda: self.updateTilesWidget())

		self.rescan()
		self.c4dTabTiles.LoadCache()

		self.openTagsWindow()
		# self.openFilterSortWindow()

		# TODO: handle this better as a first run guidance
		# Offer user to open settings
		self.openPreferencesFlag: bool = False
		if dlg:= self._getDialog('preferences'):
			if not dlg.preferencesLoaded:
				msg = QMessageBox(QMessageBox.Information, 'Empty preferences..', 'This seems to be a first run of the app. Do you want to start with configuring Search Paths in preferences?', QMessageBox.Yes | QMessageBox.No)
				if msg.exec_() == QMessageBox.Yes:
					# find search paths idx
					for idx, key in enumerate(dlg.categories.keys()):
						if key.lower() == 'search paths':
							dlg.categoriesWidget.setCurrentRow(idx)
							self.openPreferencesFlag = True
							break
	
	def _createActions(self):
		self.actionSave = QAction("&Save", self)
		self.actionSave.setShortcut(QKeySequence.Save)

		self.actionPrefs = QAction(QIcon(":preferences.svg"), "&Preferences", self)
		self.actionPrefs.setShortcut("Ctrl+E")

		self.actionExit = QAction("&Exit", self)
		self.actionAbout = QAction("&About", self)
		self.actionHelp = QAction("&Help", self)
		
		self.actionRefresh = QAction("&Refresh", self)
		self.actionRefresh.setShortcut(QKeySequence.Refresh)
		self.actionRescan = QAction("Re&scan", self)
		self.actionRescan.setShortcut("Ctrl+F5")

		self.actionTags = QAction("&Tags", self)
		self.actionTags.setShortcut("Ctrl+T")

		self.actionFiltersort = QAction("Filte&r/Sort", self)
		self.actionFiltersort.setShortcut("Ctrl+R")

		self.actionFoldAll = QAction("Toggle &fold all", self)
		self.actionFoldAll.setShortcut("Ctrl+G,Ctrl+G")

		self._createGroupActions()
		
		self.actionSave.triggered.connect(self._storeData)
		self.actionPrefs.triggered.connect(self.openPreferences)
		self.actionExit.triggered.connect(sys.exit)
		self.actionAbout.triggered.connect(self.about)
		self.actionHelp.triggered.connect(self.help)
		self.actionRefresh.triggered.connect(self.updateTilesWidget)
		self.actionRescan.triggered.connect(self.rescan)
		self.actionTags.triggered.connect(self.openTagsWindow)
		self.actionFiltersort.triggered.connect(self.openFilterSortWindow)
		self.actionFoldAll.triggered.connect(self._toggleFoldAllC4DGroups)
		
		# # Adding help tips
		# newTip = "Create a new file"
		# self.newAction.setStatusTip(newTip)
		# self.newAction.setToolTip(newTip)

	def _createGroupActions(self):
		actionsGroupingDict = { # key -> (show_txt, QColor, Shortcut)
			'none': ('&No grouping', None, 'Ctrl+G,Ctrl+N'),
			'paths': ('Group by search &folders', None, 'Ctrl+G,Ctrl+F'),
			'version': ('Group by &version', None, 'Ctrl+G,Ctrl+V'),
			'tag': ('Group by &tag', None, 'Ctrl+G,Ctrl+T'),
			'status': ('Group by &status', None, 'Ctrl+G,Ctrl+S'),
		}
		# for tag in self.GetTags():
		# 	actionsGroupingDict[f'tag:{tag.uuid}'] = (f'Group by tag \'{tag.name}\'', tag.color)

		def createCheckableAction(key: str) -> QAction:
			txt, color, shortcut = actionsGroupingDict[key]
			action: QAction = QAction(txt)
			action.setShortcut(shortcut)
			action.triggered.connect(partial(self._changeGrouping, key))
			# if color:
			# 	pixmap: QPixmap = QPixmap(20, 20)
			# 	pixmap.fill(color) # TODO: add border
			# 	action.setIcon(QIcon(pixmap))
			return action

		self.actionsGrouping: dict[str, QAction] = dict()
		for key in actionsGroupingDict.keys():
			self.actionsGrouping[key] = createCheckableAction(key)
		
		# default
		self._changeGrouping('paths')
		# self._changeGrouping('none')
		
	def _createMenuBar(self):
		menuBar = self.menuBar()
		
		fileMenu = menuBar.addMenu('&File')
		# self.openRecentMenu = fileMenu.addMenu("Open Recent")
		fileMenu.addAction(self.actionSave)
		fileMenu.addSeparator()
		fileMenu.addAction(self.actionPrefs)
		fileMenu.addSeparator()
		fileMenu.addAction(self.actionExit)
		
		editMenu = menuBar.addMenu("&Edit")
		editMenu.addAction(self.actionRefresh)
		editMenu.addAction(self.actionRescan)
		editMenu.addSeparator()
		editMenu.addAction(self.actionTags)
		editMenu.addAction(self.actionFiltersort)
		
		viewMenu = menuBar.addMenu("&View")
		viewMenu.addAction(self.actionFoldAll)
		viewMenu.addSeparator()
		for k, action in self.actionsGrouping.items():
			viewMenu.addAction(action)

		helpMenu = menuBar.addMenu("&Help")
		helpMenu.addAction(self.actionHelp)
		helpMenu.addAction(self.actionAbout)
	
	@staticmethod
	def _isActionAlreadySelected(action: QAction) -> str:
		for prefix in (MainWindow.GROUPING_MARK_ASC_PREFIX, MainWindow.GROUPING_MARK_DESC_PREFIX):
			if action.text().startswith(prefix):
				return prefix
		return ''
	def _changeGrouping(self, groupingKey: str):
		# print('group by key:', groupingKey)
		newPrefix: str = MainWindow.GROUPING_MARK_ASC_PREFIX
		# Figure out new prefix and unselect all actions to 
		for k, action in self.actionsGrouping.items():
			if curPrefix := MainWindow._isActionAlreadySelected(action):
				action.setText(action.text()[len(curPrefix):])
				if k == groupingKey:
					if curPrefix == MainWindow.GROUPING_MARK_ASC_PREFIX:
						newPrefix = MainWindow.GROUPING_MARK_DESC_PREFIX
				break
		
		for k, action in self.actionsGrouping.items():
			if k != groupingKey: continue
			action.setText(f'{newPrefix}{action.text()}')
			break
		self.updateTilesWidget()
	
	def _getGrouping(self) -> tuple[str, bool]: # <groupingKey, isAscending>
		for k, action in self.actionsGrouping.items():
			if prefix := MainWindow._isActionAlreadySelected(action):
				return k, prefix == MainWindow.GROUPING_MARK_ASC_PREFIX
		return 'none', True
	
	def _createToolBars(self):
		# fileToolBar = self.addToolBar("File")
		# fileToolBar.addAction(self.newAction)
		# fileToolBar.addAction(self.openAction)
		# fileToolBar.addAction(self.saveAction)

		# viewToolBar = self.addToolBar("View")
		# viewToolBar.addAction(self.actionPrefs)
		# viewToolBar.addAction(self.actionAbout)
		# viewToolBar.addAction(self.actionExit)
		# viewToolBar.addSeparator()
		# # Spinbox
		# self.fontSizeSpinBox = QSpinBox()
		# self.fontSizeSpinBox.setFocusPolicy(Qt.NoFocus)
		# viewToolBar.addWidget(self.fontSizeSpinBox)
		pass
	
	def _createContextMenu(self):
		pass

	def _createStatusBar(self):
		pass
	
	def _storeData(self):
		# Tags
		dlgTags: TagsWindow | None = self._getDialog('tags')
		if dlgTags:
			dlgTags.SaveTags()
		
		# C4Ds cache
		self.c4dTabTiles.SaveCache()

	def openPreferences(self):
		self._showActivateDialog('preferences')

	def about(self):
		if dlg := self._getDialog('about'):
			dlg.show()

	def help(self):
		self._showActivateDialog('help')

	def openTagsWindow(self):
		KEY = 'tags'
		if dlg := self._getDialog(KEY):
			self.addDockWidget(Qt.RightDockWidgetArea, dlg)
			self._showActivateDialog(KEY)

	def openFilterSortWindow(self):
		KEY = 'filtersort'
		if dlg := self._getDialog(KEY):
			self.addDockWidget(Qt.LeftDockWidgetArea, dlg)
			self._showActivateDialog(KEY)
	
	def _getDialog(self, dialogKey: str) -> QWidget | None:
		if dialogKey not in self.dialogs:
			return None
		return self.dialogs[dialogKey]
	
	def _showActivateDialog(self, dialogKey: str) -> QWidget | None:
		if dlg := self._getDialog(dialogKey):
			dlg.show()
			dlg.activateWindow()
			return dlg
		return None
	
	def _toggleFoldAllC4DGroups(self):
		visibilities: list[tuple[C4DTileGroup, bool]] = self.c4dTabTiles.GetGroupsVisibility()
		return self.c4dTabTiles.SetGroupsVisibility([not all([v for grp, v in visibilities])] * len(visibilities))

	def rescan(self):
		dlg: PreferencesWindow | None = self._getDialog('preferences')
		if not dlg: return print('ERROR: Preferences dialog wasn\'t found!')
		searchPaths: list[str] = dlg.GetPreference(PreferencesEntries.SearchPaths)

		c4dEntries: list[C4DInfo] = list()
		for path in searchPaths:
			if c4dsDict := FindCinemaPackagesInFolder(path):
				c4dEntries += [v for v in c4dsDict.values()]
			
		self.updateTilesWidget(c4dEntries)
	
	def updateTilesWidget(self, newC4DEntries: list[C4DInfo] | None = None):
		c4dEntries: list[C4DInfo] = newC4DEntries if newC4DEntries else self.c4dTabTiles.GetC4DEntries()

		# TODO: Below looks so much like code repetition.. clean it up!
		# Group first
		c4dGroups: list[C4DTileGroup] = list()
		groupingKey, isAscending = self._getGrouping()
		if groupingKey == 'paths':
			searchPaths: list[str] = list()
			if dlg := self._getDialog('preferences'): searchPaths = dlg.GetPreference(PreferencesEntries.SearchPaths)
			idxMap: dict[str, list[int]] = {sp: list() for sp in searchPaths}
			for c4dIdx, c4dEntry in enumerate(c4dEntries):
				for sp in searchPaths:
					if c4dEntry.directory.startswith(sp):
						idxMap[sp].append(c4dIdx)
			availablePaths: list[str] = [k for k in idxMap.keys() if idxMap[k]]
			availablePaths.sort(reverse=not isAscending)
			c4dGroups = [C4DTileGroup(idxMap[path], path) for path in availablePaths]

		elif groupingKey == 'version':
			idxMap: dict[str, list[int]] = dict()
			for c4dIdx, c4dEntry in enumerate(c4dEntries):
				vMaj: str = c4dEntry.GetVersionMajor()
				if vMaj not in idxMap: idxMap[vMaj] = list()
				idxMap[vMaj].append(c4dIdx)
			availableVersions: list[str] = [k for k in idxMap.keys()]
			availableVersions.sort(reverse=isAscending, key=lambda x: SafeCast(x[1:] if x.lower().startswith('r') else x, int, 0))
			c4dGroups = [C4DTileGroup(idxMap[version], version) for version in availableVersions]

		elif groupingKey == 'tag':
			c4dTagBinding: dict[str, list[str]] = self.c4dTabTiles.GetTagBindings()
			idxMap: dict[str, list[int]] = dict() # tag uuid -> indices
			for c4dIdx, c4dEntry in enumerate(c4dEntries):
				tagUuids: list[str] = c4dTagBinding[c4dEntry.directory]
				if not len(tagUuids):
					if '' not in idxMap: idxMap[''] = list()
					idxMap[''].append(c4dIdx)
				else:
					for tagUuid in tagUuids:
						if self.GetTag(tagUuid):
							if tagUuid not in idxMap: idxMap[tagUuid] = list()
							idxMap[tagUuid].append(c4dIdx)
			# Sort groups to correspond order in tags manager
			for tag in self.GetTags() if isAscending else reversed(self.GetTags()):
				if tag.uuid in idxMap:
					c4dGroups.append(C4DTileGroup(idxMap[tag.uuid], tag.name))
			if '' in idxMap:
				c4dGroups.append(C4DTileGroup(idxMap[''], 'No tags'))
			# c4dGroups = [C4DTileGroup(indices, self.GetTag(tagUuid).name if tagUuid else 'None') for tagUuid, indices in idxMap.items() if self.GetTag(tagUuid) or tagUuid == '']
			
		elif groupingKey == 'status':
			USE_TOUCHED_UNTOUCHED_GROUP_SPLIT = True
			keyMapNames: dict[int, str] = {
				0: 'Not started yet',
				-2: 'Killed',
				-1: 'Closed',
				1: 'Running',
				# fictive keys for labels after merging
				10: 'Untouched',
				11: 'Touched',
			}
			mergingGroups: dict[int, list[int]] = {10: [0], 11: [1, -1, -2]} # newKey -> keys in idxMap that need to be merged
			
			idxMap: dict[int, list[int]] = dict() # PID Status -> indices
			for c4dIdx, c4dEntry in enumerate(c4dEntries):
				c4dCacheInfo: C4DCacheInfo = self.c4dTabTiles.GetCacheInfo(c4dEntry.directory)
				if not c4dCacheInfo:
					continue
				statusKey: int = c4dCacheInfo.processStatus if c4dCacheInfo.processStatus <= 0 else 1 # if status > 0, it's PID -> different for all c4d entries
				if statusKey not in idxMap: idxMap[statusKey] = list()
				idxMap[statusKey].append(c4dIdx)

			if USE_TOUCHED_UNTOUCHED_GROUP_SPLIT:
				mergedIdxMap: dict[int, list[int]] = dict()
				for newKey, mergingGroup in mergingGroups.items():
					mergingIndices: list[int] = list()
					for mergingKey in mergingGroup:
						if mergingKey not in idxMap:
							continue
						mergingIndices += idxMap[mergingKey]
					mergedIdxMap[newKey] = mergingIndices
				idxMap = mergedIdxMap
			
			idxMapKeys = [key for key in keyMapNames.keys() if key in idxMap and len(idxMap[key])]
			availableStatusKeys: list[str] = [idxMapKeys[i] for i in sorted(list(range(len(idxMapKeys))), reverse=isAscending)]
			c4dGroups = [C4DTileGroup(idxMap[statusKey], keyMapNames[statusKey]) for statusKey in availableStatusKeys]

		
		# Sort
		# c4dEntries.sort(key=lambda x: GetFolderTimestampCreated(x.GetPathFolderRoot()))

		self.c4dTabTiles.updateTiles(c4dEntries, c4dGroups)
	
	def GetTags(self) -> list[C4DTag]:
		if dlgTags := self._getDialog('tags'):
			return dlgTags._getTags()
		return list()
	
	def GetTag(self, uuid: str) -> C4DTag | None:
		if dlgTags := self._getDialog('tags'):
			return dlgTags._getTag(uuid)
		return None

	def FirstRunHandler(self):
		if self.openPreferencesFlag:
			self.actionPrefs.trigger()

	def closeEvent(self, evt: QCloseEvent):
		self.hide()
		for v in self.dialogs.values():
			if v is not None:
				v.hide()
		return evt.ignore()
		for v in self.dialogs.values():
			if v is not None:
				v.close()
		evt.accept()