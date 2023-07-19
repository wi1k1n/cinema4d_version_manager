import sys, os
from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QKeySequence, QPixmap, QFont
from PyQt5.QtWidgets import (
	QApplication,
	QLabel,
	QMainWindow,
	QMenu,
	QMenuBar,
	QToolBar,
	QAction,
	QSpinBox,
	QWidget,
	QTabWidget,
	QGridLayout,
	QVBoxLayout,
	QHBoxLayout,
	QLayout,
	QFrame,
	QSizePolicy,
	QStackedLayout,
	QScrollArea
)

# import qrc_resources
from dialogs.preferences import PreferencesWindow
from dialogs.about import AboutWindow
import utils
from gui_utils import *

RES_FOLDER = os.path.join(os.getcwd(), 'res')
IMAGES_FOLDER = os.path.join(RES_FOLDER, 'icons')

class C4DEntry:
	def __init__(self, dir: str, version: str):
		self.directory: str = dir
		self.version: str = version

class C4DTile(QFrame):
	def __init__(self, c4d: C4DEntry):
		super().__init__()
		self.c4d: C4DEntry = c4d

		self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
		self.setLineWidth(1)
		self.setFixedSize(128, 128)

		print(os.getcwd())
		pic = QPixmap(os.path.join(IMAGES_FOLDER, 'C4D 2024.png'))

		picLabel: QLabel = QLabel()
		picLabel.setPixmap(pic)
		picLabel.setScaledContents(True)
		picLabel.setAlignment(Qt.AlignCenter)

		vers: QLabel = QLabel()
		vers.setText(self.c4d.version)
		vers.setFont(QFont('Comic Sans MS', 12))
		vers.setAlignment(Qt.AlignBottom)

		layout: QVBoxLayout = QVBoxLayout()
		layout.addWidget(picLabel)
		layout.addWidget(vers)
		layout.setAlignment(Qt.AlignCenter)

		self.setLayout(layout)

		picSize: int = int(min(self.width(), self.height()) * .6)
		picLabel.setFixedSize(picSize, picSize)


class C4DTilesWidget(QScrollArea):
	def __init__(self):
		super().__init__()

		self.c4dEntries: set[C4DEntry] = set()
		self.tiles = list()

		self.setWidgetResizable(True)
		self.setWidget(QWidget(self))
		self.widget().setMinimumWidth(100)

		self.tilesLayout = FlowLayout(self.widget())

		self.updateTiles(set())
	
	def updateTiles(self, c4ds: set[C4DEntry]):
		self.c4dEntries = c4ds
		self.tiles = [C4DTile(e) for e in self.c4dEntries]
		for i in reversed(range(self.tilesLayout.count())):
			self.tilesLayout.itemAt(i).widget().setParent(None)
		for w in self.tiles:
			self.tilesLayout.addWidget(w)

class MainWindow(QMainWindow):
	"""Main Window."""
	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)
		self.setWindowTitle("C4D Selector")
		self.resize(800, 600)
		self.setMinimumSize(350, 250)

		self.dialogs = {
			'preferences': PreferencesWindow(),
			'about': AboutWindow()
		}

		self.c4dTilesTab: C4DTilesWidget = C4DTilesWidget()

		self.centralWidget = QTabWidget()
		self.centralWidget.addTab(self.c4dTilesTab, "C4D Tiles")
		
		# label2 = QLabel("Widget in Tab 2.")
		# self.centralWidget.addTab(label2, "Tab 2")

		# self.centralWidget = QLabel("Hello, World")
		# self.centralWidget.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
		
		self.setCentralWidget(self.centralWidget)

		self._createActions()
		self._createMenuBar()
		self._createToolBars()
		self._createContextMenu()
		self._createStatusBar()
		self._connectActions()

		self.rescan()
		
	def _createMenuBar(self):
		menuBar = self.menuBar()
		
		fileMenu = menuBar.addMenu('&File')
		# fileMenu.addAction(self.newAction)
		# fileMenu.addAction(self.openAction)
		# self.openRecentMenu = fileMenu.addMenu("Open Recent")
		# fileMenu.addAction(self.saveAction)
		# fileMenu.addSeparator()
		fileMenu.addAction(self.actionRescan)
		fileMenu.addSeparator()
		fileMenu.addAction(self.actionPrefs)
		fileMenu.addSeparator()
		fileMenu.addAction(self.actionExit)
		
		# editMenu = menuBar.addMenu("&Edit")
		# editMenu.addAction(self.copyAction)
		# editMenu.addAction(self.pasteAction)
		# editMenu.addAction(self.cutAction)
		# editMenu.addSeparator()
		# # Find and Replace submenu in the Edit menu
		# findMenu = editMenu.addMenu("Find and Replace")
		# findMenu.addAction("Find...")
		# findMenu.addAction("Replace...")
		
		helpMenu = menuBar.addMenu("&Help")
		# helpMenu.addAction(self.helpContentAction)
		helpMenu.addAction(self.actionAbout) 
	
	def _createToolBars(self):
		# fileToolBar = self.addToolBar("File")
		# fileToolBar.addAction(self.newAction)
		# fileToolBar.addAction(self.openAction)
		# fileToolBar.addAction(self.saveAction)

		# editToolBar = self.addToolBar("Edit")
		# editToolBar.addAction(self.copyAction)
		# editToolBar.addAction(self.pasteAction)
		# editToolBar.addAction(self.cutAction)
		# editToolBar.addSeparator()
		# # Spinbox
		# self.fontSizeSpinBox = QSpinBox()
		# self.fontSizeSpinBox.setFocusPolicy(Qt.NoFocus)
		# editToolBar.addWidget(self.fontSizeSpinBox)
		pass
	
	def _createActions(self):
		self.actionPrefs = QAction(QIcon(":preferences.svg"), "&Preferences", self)
		self.actionPrefs.setShortcut("Ctrl+E")

		self.actionExit = QAction("&Exit", self)
		self.actionAbout = QAction("&About", self)
		
		self.actionRescan = QAction("&Rescan", self)
		self.actionRescan.setShortcut(QKeySequence.Refresh)
		
		# # Using string-based key sequences
		# self.newAction.setShortcut("Ctrl+N")
		# self.openAction.setShortcut("Ctrl+O")
		# self.saveAction.setShortcut("Ctrl+S")
		
		# self.copyAction.setShortcut(QKeySequence.Copy)
		# self.pasteAction.setShortcut(QKeySequence.Paste)
		# self.cutAction.setShortcut(QKeySequence.Cut)
		
		# # Adding help tips
		# newTip = "Create a new file"
		# self.newAction.setStatusTip(newTip)
		# self.newAction.setToolTip(newTip)
	
	def _createContextMenu(self):
		# Setting contextMenuPolicy
		self.centralWidget.setContextMenuPolicy(Qt.ActionsContextMenu)
		# # Populating the widget with actions
		# self.centralWidget.addAction(self.newAction)
		# self.centralWidget.addAction(self.openAction)
		# self.centralWidget.addAction(self.saveAction)
		# separator = QAction(self)
		# separator.setSeparator(True)
		# self.centralWidget.addAction(separator)
		# self.centralWidget.addAction(self.copyAction)
		# self.centralWidget.addAction(self.pasteAction)
		# self.centralWidget.addAction(self.cutAction)

	def _createStatusBar(self):
		self.statusbar = self.statusBar()
		# # Adding a temporary message
		# self.statusbar.showMessage("Ready", 3000)
		# # Adding a permanent message
		# self.wcLabel = QLabel(f"{self.getWordCount()} Words")
		# self.statusbar.addPermanentWidget(self.wcLabel)
	
	def _connectActions(self):
		# # Connect File actions
		# self.newAction.triggered.connect(self.newFile)
		# self.openAction.triggered.connect(self.openFile)
		# self.openRecentMenu.aboutToShow.connect(self.populateOpenRecent)
		# self.saveAction.triggered.connect(self.saveFile)
		self.actionPrefs.triggered.connect(self.openPreferences)
		self.actionExit.triggered.connect(self.close)
		# # Connect Edit actions
		# self.copyAction.triggered.connect(self.copyContent)
		# self.pasteAction.triggered.connect(self.pasteContent)
		# self.cutAction.triggered.connect(self.cutContent)
		# # Connect Help actions
		# self.helpContentAction.triggered.connect(self.helpContent)
		self.actionAbout.triggered.connect(self.about)

		self.actionRescan.triggered.connect(self.rescan)
	
	# def newFile(self):
	#     self.centralWidget.setText("<b>File > New</b> clicked")
	# def openFile(self):
	#     self.centralWidget.setText("<b>File > Open...</b> clicked")
	# def openRecentFile(self, filename):
	#     self.centralWidget.setText(f"<b>{filename}</b> opened")
	# def saveFile(self):
	#     self.centralWidget.setText("<b>File > Save</b> clicked")
	def openPreferences(self):
		if ('preferences' in self.dialogs):
			self.dialogs['preferences'].show()
			self.dialogs['preferences'].activateWindow()
	# def copyContent(self):
	#     self.centralWidget.setText("<b>Edit > Copy</b> clicked")
	# def pasteContent(self):
	#     self.centralWidget.setText("<b>Edit > Paste</b> clicked")
	# def cutContent(self):
	#     self.centralWidget.setText("<b>Edit > Cut</b> clicked")
	# def helpContent(self):
	#     self.centralWidget.setText("<b>Help > Help Content...</b> clicked")
	def about(self):
		# self.centralWidget.setText("<b>Help > About...</b> clicked")
		if 'about' in self.dialogs:
			self.dialogs['about'].show()
			self.dialogs['about'].activateWindow()
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
		if 'preferences' not in self.dialogs:
			return print('ERROR: Preferences dialog wasn\'t found!')
		dlg: PreferencesWindow = self.dialogs['preferences']
		searchPaths: list[str] = dlg.GetSearchPaths()
		c4dEntries: set[C4DEntry] = set()
		for path in searchPaths:
			c4dsDict: dict[str, str] | None = utils.FindCinemaPackagesInFolder(path)
			print(c4dsDict)
			if c4dsDict is None:
				continue
			c4dEntries.update([C4DEntry(p, v) for (p, v) in c4dsDict.items()])
		self.c4dTilesTab.updateTiles(c4dEntries)
	
	# def getWordCount(self):
	#     # Logic for computing the word count goes here...
	#     return 42

	def closeEvent(self, event):
		for v in self.dialogs.values():
			if v is not None:
				v.close()
		event.accept()