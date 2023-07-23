import sys, os, typing, datetime as dt
from subprocess import Popen, PIPE
from PyQt5 import QtCore, QtGui

from PyQt5.QtCore import QObject, Qt, QEvent, pyqtSignal, QProcess
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
	QProxyStyle
)

# import qrc_resources
from dialogs.preferences import PreferencesWindow, PreferencesEntries
from dialogs.about import AboutWindow
from dialogs.tags import TagsWindow, C4DTag
from dialogs.main_window_tiles import *
from utils import *
from gui_utils import *

class MainWindow(QMainWindow):
	"""Main Window."""
	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)
		
		self.c4dEntries: list[C4DInfo] = list()
		# self.c4dTags: list[C4DTag] = [
		# 	C4DTag('Favorite'),
		# 	C4DTag('Customer'),
		# 	C4DTag('Package'),
		# ]

		self.setWindowTitle("C4D Selector")
		self.resize(800, 600)
		self.setMinimumSize(350, 250)
		self.showEvent = self._onShowed

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

		self.rescan()
		self.openTags()
	
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
		
		# # Adding help tips
		# newTip = "Create a new file"
		# self.newAction.setStatusTip(newTip)
		# self.newAction.setToolTip(newTip)
		
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
		viewMenu.addAction(self.actionAbout)

		helpMenu = menuBar.addMenu("&Help")
		helpMenu.addAction(self.actionAbout)
	
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
		self.actionTags.triggered.connect(self.openTags)
	
	def _storeData(self):
		# Tags
		dlgTags: TagsWindow | None = self._getDialog('tags')
		if dlgTags:
			dlgTags.SaveTags()

	def openPreferences(self):
		self._showActivateDialog('preferences')

	def about(self):
		self._showActivateDialog('about')

	def openTags(self):
		if dlg := self._showActivateDialog('tags'):
			self.addDockWidget(Qt.RightDockWidgetArea, dlg)
	
	def _getDialog(self, dialogKey: str) -> QWidget | None:
		if dialogKey not in self.dialogs:
			return None
		return self.dialogs[dialogKey]
	
	def _showActivateDialog(self, dialogKey: str) -> QWidget | None:
		dlg: QWidget | None = self._getDialog(dialogKey)
		if dlg:
			dlg.show()
			dlg.activateWindow()
		return dlg


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
		self.c4dTabTiles.updateTiles(c4dEntries, c4dGroups)

	def _onShowed(self, evt):
		print('on show:', evt)

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