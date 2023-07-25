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
	QMessageBox
)

# import qrc_resources
from dialogs.preferences import PreferencesWindow, PreferencesEntries
from dialogs.about import AboutWindow
from dialogs.tags import TagsWindow, C4DTag
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
	"""Main Window."""
	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)

		self.setWindowTitle("C4D Selector")
		self.resize(1420, 800)
		self.setMinimumSize(350, 250)

		self.dialogs = {
			'preferences': PreferencesWindow(),
			'tags': TagsWindow(),
			'about': AboutWindow()
		}

		self.c4dTabTiles: C4DTilesWidget = C4DTilesWidget(self)

		self.c4dTabTableWidget: QTreeWidget = QTreeWidget(self)
		self.c4dTabTableWidget.setColumnCount(4)
		self.c4dTabTableWidget.setHeaderLabels(['Fav', 'Path', 'Version', 'Date'])
		for i in range(5):
			item: QTreeWidgetItem = QTreeWidgetItem(self.c4dTabTableWidget)
			for j in range(self.c4dTabTableWidget.columnCount()):
				item.setText(j, f'Col#{i}: text{j}')

		self.centralWidget = QTabWidget()
		self.centralWidget.addTab(self.c4dTabTiles, "Tiles")
		self.centralWidget.addTab(self.c4dTabTableWidget, "Table")
		
		self.setCentralWidget(self.centralWidget)

		self._createActions()
		self._createMenuBar()
		self._createToolBars()
		self._createContextMenu()
		self._createStatusBar()
		self._connectActions()

		self.dialogs['tags'].tagEditedSignal.connect(lambda tag: self.c4dTabTiles._rebuildWidget())
		self.dialogs['tags'].tagRemovedSignal.connect(lambda tag: self.c4dTabTiles._tagRemoveFromAll(tag))

		self.rescan()
		self.c4dTabTiles.LoadCache()

		self.openTagsWindow()

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
		
		self.actionRescan = QAction("&Rescan", self)
		self.actionRescan.setShortcut(QKeySequence.Refresh)

		self.actionTags = QAction("&Tags", self)
		self.actionTags.setShortcut("Ctrl+T")

		self._createGroupActions()
		
		# # Adding help tips
		# newTip = "Create a new file"
		# self.newAction.setStatusTip(newTip)
		# self.newAction.setToolTip(newTip)

	def _createGroupActions(self):
		actionsGroupingDict = { # key -> (show_txt, QColor)
			'none': ('&No grouping', None),
			'paths': ('Group by &search paths', None),
			'version': ('Group by &version', None),
			'versionmaj': ('Group by version &major', None),
		}
		for tag in self.GetTags():
			actionsGroupingDict[f'tag:{tag.name}'] = (f'Group by tag \'{tag.name}\'', tag.color)

		def createCheckableAction(key: str) -> QAction:
			txt, color = actionsGroupingDict[key]
			action: QAction = QAction(txt)
			# action.setCheckable(True)
			# action.setChecked(False)
			action.triggered.connect(partial(self._changeGrouping, key))
			if color:
				pixmap: QPixmap = QPixmap(20, 20)
				pixmap.fill(color) # TODO: add border
				action.setIcon(QIcon(pixmap))
			return action

		self.actionsGrouping: dict[str, QAction] = dict()
		for key in actionsGroupingDict.keys():
			self.actionsGrouping[key] = createCheckableAction(key)
		
		# default
		self._changeGrouping('paths')
		
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
		editMenu.addAction(self.actionRescan)
		editMenu.addSeparator()
		editMenu.addAction(self.actionTags)
		
		viewMenu = menuBar.addMenu("&View")
		for k, action in self.actionsGrouping.items():
			viewMenu.addAction(action)

		helpMenu = menuBar.addMenu("&Help")
		helpMenu.addAction(self.actionAbout)
	
	def _changeGrouping(self, groupingKey: str):
		print('group by key:', groupingKey)
		MARK_PREFIX: str = '► '
		for k, action in self.actionsGrouping.items():
			alreadyMarked: bool = action.text().startswith(MARK_PREFIX)
			if k == groupingKey:
				if not alreadyMarked:
					action.setText(f'{MARK_PREFIX}{action.text()}')
				continue
			if alreadyMarked:
				action.setText(action.text()[2:])
	
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
	
	def _connectActions(self):
		self.actionSave.triggered.connect(self._storeData)
		self.actionPrefs.triggered.connect(self.openPreferences)
		self.actionExit.triggered.connect(sys.exit)
		self.actionAbout.triggered.connect(self.about)
		self.actionRescan.triggered.connect(self.rescan)
		self.actionTags.triggered.connect(self.openTagsWindow)
	
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
		self._showActivateDialog('about')

	def openTagsWindow(self):
		KEY = 'tags'
		if dlg := self._getDialog(KEY):
			self.addDockWidget(Qt.RightDockWidgetArea, dlg)
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

	# def populateOpenRecent(self):
	#     # Step 1. Remove the old options from the menu
	#     self.openRecentMenu.clear()
	#     # Step 2. Dynamically create the actions
	#     actions = []
	#     filenames = [f"File-{n}" for n in range(5)]
	#     for filename in filenames:
	#         action = QAction(filename, self)
	#         action.triggered.connect(partial(self.openRecentFile, filename))
	#         actions.append(action)
	#     # Step 3. Add the actions to the menu
	#     self.openRecentMenu.addActions(actions)

	def rescan(self):
		dlg: PreferencesWindow | None = self._getDialog('preferences')
		if not dlg: return print('ERROR: Preferences dialog wasn\'t found!')
		
		searchPaths: list[str] = dlg.GetPreference(PreferencesEntries.SearchPaths)
		c4dEntries: list[C4DInfo] = list()
		c4dGroups: list[C4DTileGroup] = list()
		for path in searchPaths:
			c4dsDict: dict[str, C4DInfo] | None = FindCinemaPackagesInFolder(path)
			if c4dsDict is None:
				continue
			offs: int = len(c4dEntries)
			# c4dGroups.append(C4DTileGroup([i + offs for i in range(len(c4dsDict))], path))
			c4dEntries += [v for v in c4dsDict.values()]
		# self.c4dTabTiles.updateTiles([c for c in c4dEntries if c.directory == 'C:/Program Files\\Maxon Cinema 4D 2023'], c4dGroups)
		c4dEntries.sort(key=lambda x: GetFolderTimestampCreated(x.GetPathFolderRoot()))
		self.c4dTabTiles.updateTiles(c4dEntries, c4dGroups)
	
	def GetTags(self) -> list[C4DTag]:
		if dlgTags := self._getDialog('tags'):
			return dlgTags._getTags()
		return list()
	
	def GetTag(self, uuid: str) -> C4DTag | None:
		if dlgTags := self._getDialog('tags'):
			return dlgTags._getTag(uuid)
		return None

	# def _onShowed(self, evt):

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