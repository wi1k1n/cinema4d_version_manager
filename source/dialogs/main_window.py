import sys, os, datetime as dt
from subprocess import Popen, PIPE

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QKeySequence, QPixmap, QFont, QCursor, QMouseEvent
from PyQt5.QtWidgets import (
	QApplication,
	QLabel,
	QMainWindow,
	QMenu, QMenuBar,
	QToolBar,
	QAction,
	QWidget,
	QTabWidget,
	QLayout, QVBoxLayout, QHBoxLayout,
	QFrame,
	QScrollArea,
	QGroupBox,
)

# import qrc_resources
from dialogs.preferences import PreferencesWindow
from dialogs.about import AboutWindow
from utils import *
from gui_utils import *

RES_FOLDER = os.path.join(os.getcwd(), 'res')
IMAGES_FOLDER = os.path.join(RES_FOLDER, 'images')
C4D_ICONS_FOLDER = os.path.join(IMAGES_FOLDER, 'c4d')

class C4DTile(QFrame):
	def __init__(self, c4d: C4DInfo):
		super().__init__()
		self.c4d: C4DInfo = c4d

		self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
		self.setLineWidth(1)
		self.setFixedSize(100, 100)

		# Many thanks to Ronald for the icons: https://backstage.maxon.net/topic/3064/cinema-4d-icon-pack
		c4dIconName: str = 'C4D ' + self.c4d.GetVersionMajor() + '.png'
		c4dIconPath: str = os.path.join(C4D_ICONS_FOLDER, c4dIconName)
		pic = QPixmap(c4dIconPath if os.path.isfile(c4dIconPath) else os.path.join(C4D_ICONS_FOLDER, 'Color Purple.png'))

		picLabel: QLabel = QLabel()
		picLabel.setPixmap(pic)
		picLabel.setScaledContents(True)
		picLabel.setCursor(QCursor(Qt.PointingHandCursor))

		versLabel: QLabel = QLabel(self.c4d.GetVersionString())
		versLabel.setFont(QFont('SblHebrew', 12))
		versLabel.setAlignment(Qt.AlignHCenter)

		tDt: dt.datetime = GetFolderTimestampCreated(self.c4d.GetPathFolderRoot())
		folderLabel: QLabel = QLabel(self.c4d.GetNameFolderRoot() + '\n' + tDt.strftime('%d/%m/%Y %H:%M'))
		folderLabel.setWordWrap(True)
		folderLabel.setFont(QFont('SblHebrew', 6))

		layout: QVBoxLayout = QVBoxLayout()
		layout.addWidget(folderLabel)
		layout.addWidget(picLabel)
		layout.addWidget(versLabel)
		layout.setAlignment(Qt.AlignCenter)

		self.setLayout(layout)

		picSize: int = int(min(self.width(), self.height()) * .6)
		picLabel.setFixedSize(picSize, picSize)

		self.setToolTip(self._createTooltipMenuString())
		
		self._addActions()
		picLabel.mousePressEvent = self._mouseClicked

		self.setContextMenuPolicy(Qt.CustomContextMenu)
		self.customContextMenuRequested.connect(self._contextMenuRequested)
	
	def _mouseClicked(self, evt: QMouseEvent):
		if evt.button() == Qt.LeftButton:
			if evt.modifiers() & Qt.KeyboardModifier.ControlModifier:
				if evt.modifiers() & Qt.KeyboardModifier.ShiftModifier: 	# Ctrl+Shift+Click: open prefs folder
					self.actionOpenFolderPrefs.trigger()
				else: 														# Ctrl+Click: run with console
					self.actionRunC4DConsole.trigger()
			elif evt.modifiers() & Qt.KeyboardModifier.ShiftModifier: 		# Shift+Click: open c4d folder
				self.actionOpenFolder.trigger()
			else: 															# Click: run c4d
				self.actionRunC4D.trigger()
		pass

	def _runC4D(self, args: list[str] = []):
		p = Popen([self.c4d.GetPathExecutable()] + args)
		print(p.pid)

	def _createTooltipMenuString(self):
		return f'{self.c4d.GetPathFolderRoot()}'
	
	def _addActions(self):
		self.actionRunC4D = QAction('Run C4D')
		self.actionRunC4D.triggered.connect(lambda: self._runC4D())
		self.actionRunC4DConsole = QAction('Run C4D w/console')
		self.actionRunC4DConsole.triggered.connect(lambda: self._runC4D(['g_console=true']))
		self.actionOpenFolder = QAction('Open folder')
		self.actionOpenFolder.triggered.connect(lambda: OpenFolderInDefaultExplorer(self.c4d.GetPathFolderRoot()))
		self.actionOpenFolderPrefs = None
		if self.c4d.GetPathFolderPrefs():
			self.actionOpenFolderPrefs = QAction('Open folder prefs')
			self.actionOpenFolderPrefs.triggered.connect(lambda: OpenFolderInDefaultExplorer(self.c4d.GetPathFolderPrefs()))

	def _contextMenuRequested(self):
		menu = QtWidgets.QMenu()

		menu.addAction(self.actionRunC4D)
		menu.addAction(self.actionRunC4DConsole)
		menu.addSeparator()
		menu.addAction(self.actionOpenFolder)
		if self.actionOpenFolderPrefs:
			menu.addAction(self.actionOpenFolderPrefs)

		menu.exec_(QtGui.QCursor.pos())

class C4DTileGroup:
	def __init__(self, indices: list[int] = list(), name: str = '') -> None:
		self.indices = indices
		self.name = name

class C4DTilesWidget(QScrollArea):
	def __init__(self):
		super().__init__()

		self.c4dEntries: list[C4DInfo] = list()

		self.setWidgetResizable(True)

		self.updateTiles([])
	
	def updateTiles(self, c4ds: list[C4DInfo], grouping: list[C4DTileGroup] | None = None):
		self.c4dEntries = c4ds

		c4dGroups: list[C4DTileGroup] = [C4DTileGroup()]
		if grouping is not None:
			c4dGroups = grouping
		if not len(c4dGroups):
			c4dGroups = [C4DTileGroup()]

		if self.widget(): self.widget().deleteLater()

		groupsLayout: QVBoxLayout = QVBoxLayout()
		centralWidget: QWidget = QWidget(self)
		centralWidget.setLayout(groupsLayout)
		centralWidget.setMinimumWidth(100)
		self.setWidget(centralWidget)

		# Populate
		for grp in c4dGroups:
			flowLayout: FlowLayout = FlowLayout()
			indices = grp.indices
			if not len(indices): indices = [i for i in range(len(self.c4dEntries))]
			for idx in indices:
				flowLayout.addWidget(C4DTile(self.c4dEntries[idx]))

			createGroup: bool = len(grp.name)
			curWidget: QWidget
			if createGroup:
				curWidget = QGroupBox(grp.name)
			else:
				curWidget = QWidget()
			curWidget.setLayout(flowLayout)
			groupsLayout.addWidget(curWidget)
		
		groupsLayout.addStretch()

class MainWindow(QMainWindow):
	"""Main Window."""
	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)
		self.c4dEntries: list[C4DInfo] = list()

		self.setWindowTitle("C4D Selector")
		self.resize(800, 600)
		self.setMinimumSize(350, 250)

		self.dialogs = {
			'preferences': PreferencesWindow(),
			'about': AboutWindow()
		}

		self.c4dTabTiles: C4DTilesWidget = C4DTilesWidget()
		self.c4dTabTableWidget: QLabel = QLabel('Table')

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
	
	def _createActions(self):
		self.actionPrefs = QAction(QIcon(":preferences.svg"), "&Preferences", self)
		self.actionPrefs.setShortcut("Ctrl+E")

		self.actionExit = QAction("&Exit", self)
		self.actionAbout = QAction("&About", self)
		
		self.actionRescan = QAction("&Rescan", self)
		self.actionRescan.setShortcut(QKeySequence.Refresh)
		
		# # Adding help tips
		# newTip = "Create a new file"
		# self.newAction.setStatusTip(newTip)
		# self.newAction.setToolTip(newTip)
		
	def _createMenuBar(self):
		menuBar = self.menuBar()
		
		fileMenu = menuBar.addMenu('&File')
		# self.openRecentMenu = fileMenu.addMenu("Open Recent")
		fileMenu.addAction(self.actionRescan)
		fileMenu.addSeparator()
		fileMenu.addAction(self.actionPrefs)
		fileMenu.addSeparator()
		fileMenu.addAction(self.actionExit)
		
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
		self.statusbar = self.statusBar()
		self.statusbar.showMessage("Scan", 500)
	
	def _connectActions(self):
		self.actionPrefs.triggered.connect(self.openPreferences)
		self.actionExit.triggered.connect(self.close)
		self.actionAbout.triggered.connect(self.about)
		self.actionRescan.triggered.connect(self.rescan)
	
	def openPreferences(self):
		if 'preferences' in self.dialogs:
			dlg: PreferencesWindow = self.dialogs['preferences']
			dlg.show()
			dlg.activateWindow()
	def about(self):
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
		c4dEntries: set[C4DInfo] = set()
		for path in searchPaths:
			c4dsDict: dict[str, C4DInfo] | None = FindCinemaPackagesInFolder(path)
			if c4dsDict is None:
				continue
			c4dEntries.update([v for v in c4dsDict.values()])
		self.c4dTabTiles.updateTiles(list(c4dEntries), [
				C4DTileGroup([0, 1, 2, 3, 4, 5], 'Large'),
				C4DTileGroup([3, 4, 5])
			])

	def closeEvent(self, event):
		for v in self.dialogs.values():
			if v is not None:
				v.close()
		event.accept()