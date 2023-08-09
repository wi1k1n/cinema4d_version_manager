import sys, os, typing, datetime as dt
from subprocess import Popen, PIPE
from functools import partial
from typing import Callable

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import (
    QObject, Qt, QEvent, pyqtSignal, QProcess, QPoint, QRect
)
from PyQt5.QtGui import (
    QIcon, QKeySequence, QPixmap, QFont, QCursor, QMouseEvent, QDropEvent,
    QDragEnterEvent, QKeyEvent, QCloseEvent
)
from PyQt5.QtWidgets import (
	QApplication, QLabel, QMainWindow, QMenu, QMenuBar, QStyle, QStyleHintReturn, QStyleOption,
	QToolBar, QAction, QWidget, QTabWidget, QLayout, QVBoxLayout, QHBoxLayout, QFrame,
	QScrollArea, QGroupBox, QTreeWidget, QTreeWidgetItem, QStatusBar, QProxyStyle, QMessageBox,
)

# import qrc_resources
from dialogs.preferences import PreferencesWindow
from dialogs.about import AboutWindow
from dialogs.help import ShortcutsWindow
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

	hideToTraySignal = pyqtSignal()

	"""Main Window."""
	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)

		self.setWindowTitle("C4D Version Manager")
		self.resize(1420, 840)
		self.setMinimumSize(350, 250)

		self.dialogs = {
			'preferences': PreferencesWindow(self),
			'tags': TagsWindow(),
			'filtersort': FilterSortWindow(),
			'about': AboutWindow(self),
			'help': ShortcutsWindow(self),
		}

		self.c4dTabTiles: C4DTilesWidget = C4DTilesWidget(self)
		self.c4dTabTiles.c4dStatusChanged.connect(self._onC4DStatusChanged)
		self.c4dTabTiles.mouseDoubleClickedSignal.connect(self._onC4DTabTilesMouseDoubleClick)

		# self.c4dTabTableWidget: QTreeWidget = QTreeWidget(self)
		# self.c4dTabTableWidget.setColumnCount(4)
		# self.c4dTabTableWidget.setHeaderLabels(['Fav', 'Path', 'Version', 'Date'])
		# for i in range(5):
		# 	item: QTreeWidgetItem = QTreeWidgetItem(self.c4dTabTableWidget)
		# 	for j in range(self.c4dTabTableWidget.columnCount()):
		# 		item.setText(j, f'Col#{i}: text{j}')

		# Stacked widget for tiles, to show no-search-paths disclaimer
		noSearchPathsDisclaimerLabel: QLabel = QLabel('No C4D instances found!\n\nAdjust paths in preferences and Rescan (Ctrl + F5)', self)
		noSearchPathsDisclaimerLabel.setAlignment(Qt.AlignCenter)
		noSearchPathsDisclaimerLabel.setFont(QFont(APPLICATION_FONT_FAMILY, 18))
		self.c4dTilesStackedContainer: QStackedWidget = QStackedWidget(self)
		self.c4dTilesStackedContainer.addWidget(noSearchPathsDisclaimerLabel)
		self.c4dTilesStackedContainer.addWidget(self.c4dTabTiles)

		self.centralWidget = QTabWidget()
		self.centralWidget.addTab(self.c4dTilesStackedContainer, "Tiles")
		# self.centralWidget.addTab(self.c4dTabTableWidget, "Table")
		
		self.setCentralWidget(self.centralWidget)

		self._createActions()
		self._createMenuBar()
		self._createToolBars()
		self._createContextMenu()
		self._createStatusBar()

		self.dialogs['preferences'].preferenceChangedSignal.connect(self._onPreferenceChanged)
		self.dialogs['tags'].tagEditedSignal.connect(lambda tag: self.c4dTabTiles._rebuildWidget())
		self.dialogs['tags'].tagRemovedSignal.connect(lambda tag: self.c4dTabTiles._tagRemoveFromAll(tag))
		self.dialogs['tags'].tagOrderChangedSignal.connect(lambda: self.updateTilesWidget())
		self.dialogs['tags'].groupingByTagRequested.connect(self._groupByTagRequested)

		self.rescan()
		self.c4dTabTiles.LoadCache()

		self.addDockWidget(Qt.LeftDockWidgetArea, self.dialogs['filtersort'])
		self.dialogs['filtersort'].hide()
		# self.toggleOpenFilterSortWindow()
		self.addDockWidget(Qt.RightDockWidgetArea, self.dialogs['tags'])
		self.toggleOpenTagsWindow()

		# TODO: handle this better as a first run guidance
		# Offer user to open settings
		self.openPreferencesFlag: bool = False
		if dlg := self._getDialog('preferences'):
			if not dlg.IsPreferencesLoaded():
				# find search paths idx
				for idx, key in enumerate(dlg.categories.keys()):
					if key.lower() == 'search paths': # bad design!
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
		self.actionShortcuts = QAction("&Shortcuts", self)
		self.actionShortcuts.setShortcut("F1")
		
		self.actionRefresh = QAction("&Refresh", self)
		self.actionRefresh.setShortcut(QKeySequence.Refresh)
		self.actionRescan = QAction("Re&scan", self)
		self.actionRescan.setShortcut("Ctrl+F5")

		self.actionTags = QAction("&Tags", self)
		self.actionTags.setShortcut("Ctrl+T")

		self.actionFiltersort = QAction("Filte&r/Sort", self)
		self.actionFiltersort.setShortcut("Ctrl+F")

		self.actionFoldAll = QAction("Toggle &fold all", self)
		self.actionFoldAll.setShortcut("Ctrl+A")

		self._createGroupActions()
		
		self.actionSave.triggered.connect(self._storeData)
		self.actionPrefs.triggered.connect(self.openPreferences)
		self.actionExit.triggered.connect(sys.exit)
		self.actionAbout.triggered.connect(self.about)
		self.actionShortcuts.triggered.connect(self.help)
		self.actionRefresh.triggered.connect(lambda: self.updateTilesWidget())
		self.actionRescan.triggered.connect(self.rescan)
		self.actionTags.triggered.connect(self.toggleOpenTagsWindow)
		self.actionFiltersort.triggered.connect(self.toggleOpenFilterSortWindow)
		self.actionFoldAll.triggered.connect(self._toggleFoldAllC4DGroups)
		
		# # Adding help tips
		# newTip = "Create a new file"
		# self.newAction.setStatusTip(newTip)
		# self.newAction.setToolTip(newTip)

	def _createGroupActions(self):
		actionsGroupingDict = { # key -> (show_txt, QColor, Shortcut)
			'none': ('&No grouping', None, ['Ctrl+G,Ctrl+G']),
			'paths': ('Group by search &folders', None, ['Ctrl+G,Ctrl+F', 'Ctrl+1']),
			'version': ('Group by &version', None, ['Ctrl+G,Ctrl+V', 'Ctrl+2']),
			'tag': ('Group by &tag', None, ['Ctrl+G,Ctrl+T', 'Ctrl+3']),
			'status': ('Group by &status', None, ['Ctrl+G,Ctrl+S', 'Ctrl+4']),
		}
		# for tag in self.GetTags():
		# 	actionsGroupingDict[f'tag:{tag.uuid}'] = (f'Group by tag \'{tag.name}\'', tag.color)

		def createCheckableAction(key: str) -> QAction:
			txt, color, shortcuts = actionsGroupingDict[key]
			action: QAction = QAction(txt)
			action.setShortcuts(shortcuts)
			action.triggered.connect(partial(self._changeGrouping, key, True))
			# if color:
			# 	pixmap: QPixmap = QPixmap(20, 20)
			# 	pixmap.fill(color) # TODO: add border
			# 	action.setIcon(QIcon(pixmap))
			return action

		self.actionsGrouping: dict[str, QAction] = dict()
		for key in actionsGroupingDict.keys():
			self.actionsGrouping[key] = createCheckableAction(key)
		
		# default
		self._changeGrouping('paths', False)
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
		helpMenu.addAction(self.actionShortcuts)
		helpMenu.addAction(self.actionAbout)
	
	@staticmethod
	def _isActionAlreadySelected(action: QAction) -> str:
		for prefix in (MainWindow.GROUPING_MARK_ASC_PREFIX, MainWindow.GROUPING_MARK_DESC_PREFIX):
			if action.text().startswith(prefix):
				return prefix
		return ''
	
	def _changeGrouping(self, groupingKey: str, toggleSort: bool):
		newPrefix: str = MainWindow.GROUPING_MARK_ASC_PREFIX
		# Figure out new prefix and unselect all actions to 
		for k, action in self.actionsGrouping.items():
			if curPrefix := MainWindow._isActionAlreadySelected(action):
				action.setText(action.text()[len(curPrefix):])
				if k == groupingKey:
					if not toggleSort:
						newPrefix = curPrefix
						break
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

	def toggleOpenTagsWindow(self):
		self.toggleOpenWindow('tags')

	def toggleOpenFilterSortWindow(self):
		self.toggleOpenWindow('filtersort')
	
	def toggleOpenWindow(self, windowKey: str):
		if dlg := self._getDialog(windowKey):
			if dlg.isVisible():
				dlg.hide()
			else:
				self._showActivateDialog(windowKey)
	
	def _getDialog(self, dialogKey: str) -> QWidget | None:
		if dialogKey not in self.dialogs:
			return None
		return self.dialogs[dialogKey]
	
	def GetPreference(self, prefKey: str) -> Any:
		if dlg := self._getDialog('preferences'):
			return dlg.GetPreference(prefKey)
		return None
	
	def _onPreferenceChanged(self, attr: str):
		if attr == 'general_hide-on-close':
			return
		if   attr == 'appearance_ronalds-icons' \
		  or attr == 'appearance_c4dtile-adjust-c4d-folder-name' \
		  or attr == 'appearance_c4dtile-show-timestamp' \
		  or attr == 'appearance_c4dtile-timestamp-format' \
		  or attr == 'appearance_c4dtile-show-note' \
		  or attr == 'appearance_c4dtile-show-note-first-line':
			return self.c4dTabTiles.UpdateTilesUI()
		if attr == 'appearance_grouping-status-separately':
			return self.updateTilesWidget()
		print('Unhandled preference change event:', attr)
	
	def _showActivateDialog(self, dialogKey: str) -> QWidget | None:
		if dlg := self._getDialog(dialogKey):
			dlg.show()
			dlg.activateWindow()
			return dlg
		return None
	
	def _onC4DStatusChanged(self, info, status):
		self.updateTilesWidget() # update tiles if c4d status was changed
	
	def _onC4DTabTilesMouseDoubleClick(self, evt: QMouseEvent):
		self._changeGrouping('paths', False)
		self._setFoldAllC4DGroups(False)
	
	def _groupByTagRequested(self, tag: C4DTag):
		if tag is None:
			return
		groupingKey, _ = self._getGrouping()
		if groupingKey != 'tag':
			self._changeGrouping('tag', False)
		visibilities: dict[C4DTileGroup, bool] = self.c4dTabTiles.GetGroupsVisibility()
		if visibleGroups := [grp for grp in visibilities.keys() if grp.key == tag]:
			grp: C4DTileGroup = visibleGroups[0]
			return self.c4dTabTiles.SetGroupsVisibility({k: k == grp for k in visibilities.keys()})

	def _toggleFoldAllC4DGroups(self):
		visibilities: dict[C4DTileGroup, bool] = self.c4dTabTiles.GetGroupsVisibility()
		val: bool = all(visibilities.values())
		return self.c4dTabTiles.SetGroupsVisibility({grp: not val for grp in visibilities.keys()})
	
	def _setFoldAllC4DGroups(self, val: bool):
		visibilities: dict[C4DTileGroup, bool] = self.c4dTabTiles.GetGroupsVisibility()
		return self.c4dTabTiles.SetGroupsVisibility({grp: not val for grp in visibilities.keys()})

	def rescan(self):
		searchPaths: list[str] = self.GetPreference('search-paths_search-paths')
		if searchPaths is None: searchPaths = list()

		c4dEntries: list[C4DInfo] = list()
		for path in searchPaths:
			if c4dsDict := FindCinemaPackagesInFolder(path):
				c4dEntries += [v for v in c4dsDict.values()]
			
		self.updateTilesWidget(c4dEntries)
		self.c4dTilesStackedContainer.setCurrentIndex(1 if c4dEntries else 0)
	
	def updateTilesWidget(self, newC4DEntries: list[C4DInfo] | None = None, visibilityCallback: Callable[[dict[C4DTileGroup, bool]], None] | None = None):
		# TODO: Below looks so much like code repetition.. clean it up!
		
		c4dEntries: list[C4DInfo] = newC4DEntries if newC4DEntries is not None else self.c4dTabTiles.GetC4DEntries()
		currentVisibilities: dict[C4DTileGroup, bool] = self.c4dTabTiles.GetGroupsVisibility()
		currentGrouping: str = self.oldGroupingKey if hasattr(self, 'oldGroupingKey') and self.oldGroupingKey else ''
		
		# Group first
		c4dGroups: list[C4DTileGroup] = list()
		groupingKey, isAscending = self._getGrouping()
		if groupingKey == 'paths':
			searchPaths: list[str] = self.GetPreference('search-paths_search-paths')
			if searchPaths is None: searchPaths = list()
			idxMap: dict[str, list[int]] = {sp: list() for sp in searchPaths} # path -> indices
			for c4dIdx, c4dEntry in enumerate(c4dEntries):
				for sp in searchPaths:
					if c4dEntry.directory.startswith(sp):
						idxMap[sp].append(c4dIdx)
			availablePaths: list[str] = [k for k in idxMap.keys() if idxMap[k]]
			availablePaths.sort(reverse=not isAscending)
			c4dGroups = [C4DTileGroup(idxMap[path], path, path) for path in availablePaths]

		elif groupingKey == 'version':
			idxMap: dict[str, tuple[list[int], str]] = dict() # major_version -> <indices, non-formatted_version>
			for c4dIdx, c4dEntry in enumerate(c4dEntries):
				vMaj: str = c4dEntry.GetVersionMajor()
				if vMaj not in idxMap: idxMap[vMaj] = (list(), c4dEntry.GetVersionString(False, True))
				idxMap[vMaj][0].append(c4dIdx)
			availableVersions: list[str] = [k for k in idxMap.keys()]
			availableVersions.sort(reverse=isAscending, key=lambda x: SafeCast(x[1:] if x.lower().startswith('r') else x, int, 0))
			c4dGroups = [C4DTileGroup(idxMap[version][0], version, idxMap[version][1]) for version in availableVersions]

		elif groupingKey == 'tag':
			c4dTagBinding: dict[str, list[str]] = self.c4dTabTiles.GetTagBindings()
			idxMap: dict[str, tuple[list[int], C4DTag | None]] = dict() # tag uuid -> <indices, tag | None>
			for c4dIdx, c4dEntry in enumerate(c4dEntries):
				tagUuids: list[str] = c4dTagBinding[c4dEntry.directory]
				if not len(tagUuids):
					if '' not in idxMap: idxMap[''] = (list(), None)
					idxMap[''][0].append(c4dIdx)
				else:
					for tagUuid in tagUuids:
						if tag := self.GetTag(tagUuid):
							if tagUuid not in idxMap: idxMap[tagUuid] = (list(), tag)
							idxMap[tagUuid][0].append(c4dIdx)
			# Sort groups to correspond order in tags manager
			for tag in self.GetTags() if isAscending else reversed(self.GetTags()):
				if tag.uuid in idxMap:
					c4dGroups.append(C4DTileGroup(idxMap[tag.uuid][0], tag.name, idxMap[tag.uuid][1]))
			if '' in idxMap:
				c4dGroups.append(C4DTileGroup(idxMap[''][0], 'No tags'))
			# c4dGroups = [C4DTileGroup(indices, self.GetTag(tagUuid).name if tagUuid else 'None') for tagUuid, indices in idxMap.items() if self.GetTag(tagUuid) or tagUuid == '']
			
		elif groupingKey == 'status':
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

			if self.GetPreference('appearance_grouping-status-separately') == 0: # group touched
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
			c4dGroups = [C4DTileGroup(idxMap[statusKey], keyMapNames[statusKey], statusKey) for statusKey in availableStatusKeys]

		# Sort
		# c4dEntries.sort(key=lambda x: GetFolderTimestampCreated(x.GetPathFolderRoot()))

		# Create tiles
		self.c4dTabTiles.updateTiles(c4dEntries, c4dGroups)
		
		# Handle groups visibility
		if visibilityCallback is not None: # explicitly set what should be visible
			visibilityFlags: dict[C4DTileGroup, bool] = {grp: True for grp in c4dGroups}
			visibilityCallback(visibilityFlags)
			self.c4dTabTiles.SetGroupsVisibility(visibilityFlags)
		elif currentGrouping == groupingKey: # grouping key hasn't changed -> keep current visibilities
			self.c4dTabTiles.SetGroupsVisibility(currentVisibilities)
			self.currentGrouping = ''
		
		self.oldGroupingKey = groupingKey

	
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
		if self.GetPreference('general_hide-on-close'):
			self.hide()
			for v in self.dialogs.values():
				if v is not None:
					v.hide()
			self.hideToTraySignal.emit()
			return evt.ignore()
		
		for v in self.dialogs.values():
			if v is not None:
				v.close()
		evt.accept()