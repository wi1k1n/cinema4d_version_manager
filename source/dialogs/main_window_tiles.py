import sys, os, typing, datetime as dt, json, re
from subprocess import Popen, PIPE
from functools import partial

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QObject, Qt, QEvent, pyqtSignal, QProcess, QRect, QPoint, QPropertyAnimation
from PyQt5.QtGui import QIcon, QKeySequence, QPixmap, QFont, QCursor, QMouseEvent, QDropEvent, QDragEnterEvent, QKeyEvent, QCloseEvent, QPaintEvent, QPainter, QColor, QBrush, QPen
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
	QInputDialog,
	QPlainTextEdit,
	QShortcut,
	QMessageBox,
)

# import qrc_resources
from dialogs.preferences import PreferencesWindow
from dialogs.about import AboutWindow
from dialogs.tags import TagsWindow, C4DTag, TagBubbleWidget
from version import *
from utils import *
from gui_utils import *


# # TODO: here for now, please remove once not needed!
# class C4DTile2(QWidget):
# 	def __init__(self, c4d: C4DInfo, parent: QWidget | None = None) -> None:
# 		super().__init__(parent)

# 		self.setFixedSize(100, 100)
# 		self.pixMap: QPixmap = QPixmap(os.path.join(C4D_ICONS_FOLDER, 'Color Purple.png'))
		

# 	def paintEvent(self, evt: QPaintEvent) -> None:
# 		p: QPainter = QPainter(self)

# 		p.fillRect(self.rect(), QBrush(Qt.red, Qt.Dense5Pattern))

# 		p.drawPixmap(QRect(0, 0, 60, 60), self.pixMap)

# 		p.setFont(QFont('Comic', 18))
# 		p.drawText(self.rect(), Qt.AlignLeft | Qt.AlignVCenter, 'Hello world!')

# 		return super().paintEvent(evt)

class NoteEditorDialog(QDialog):
	def __init__(self, title: str = 'Edit text', initialText: str = '', parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self.setWindowTitle(title)
		
		self.editNote: QPlainTextEdit = QPlainTextEdit(initialText, self)
		buttons: QDialogButtonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
		buttons.accepted.connect(self.accept)
		buttons.rejected.connect(self.close)

		formLayout = QFormLayout()
		formLayout.addWidget(self.editNote)
		formLayout.addWidget(buttons)

		self.setLayout(formLayout)

		self.editNote.installEventFilter(self)
	
	def GetNoteText(self) -> str:
		return self.editNote.toPlainText()
	
	def eventFilter(self, obj: QObject, evt: QEvent) -> bool:
		if evt.type() in (evt.Type.KeyPress, evt.Type.ShortcutOverride):
			if evt.key() == Qt.Key_Return and evt.modifiers() == Qt.KeyboardModifier.ControlModifier:
				evt.ignore()
				self.accept()
				return True
		return super().eventFilter(obj, evt)

class C4DTile(QFrame):
	# https://forum.qt.io/topic/90403/show-tooltip-immediatly/6
	class C4DTileProxyStyle(QProxyStyle):
		def styleHint(self, hint: QStyle.StyleHint, option: QStyleOption | None = None, widget: QWidget | None = None, returnData: QStyleHintReturn | None = None) -> int:
			if hint == QStyle.SH_ToolTip_WakeUpDelay:
				return 0
			return super().styleHint(hint, option, widget, returnData)

	c4dStatusChanged = pyqtSignal(int)
	def __init__(self, c4d: C4DInfo, parent: QWidget | None = None) -> None:
		self.parentTilesWidget = parent # TODO: this is bad design!!
		super().__init__(parent)

		self.c4d: C4DInfo = c4d

		# TODO: separate this in a class to not mess around with the scope here
		self.c4dProcess: QProcess = QProcess()
		# self.c4dProcess.setStandardErrorFile(QProcess.nullDevice())
		# self.c4dProcess.setStandardInputFile(QProcess.nullDevice())
		# self.c4dProcess.setStandardOutputFile(QProcess.nullDevice())
		self.c4dProcessArgs = []
		self.c4dProcessRestartTime: QTimer = QTimer()
		self.c4dProcessRestartTime.setInterval(500)
		self.c4dProcessRestartTime.setSingleShot(True)
		self.c4dProcessRestartTime.timeout.connect(lambda: self._runC4D(self.c4dProcessArgs))

		self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
		self.setLineWidth(1)
		# self.setFixedSize(100, 100)
		self.setAcceptDrops(True)
		# self.setMouseTracking(True)
		self.setStyle(C4DTile.C4DTileProxyStyle())

		self._setupUI()
		self._addActions()
		
		self.setToolTip(self._createTooltipMenuString())
		self.picLabel.mousePressEvent = self._mouseClicked

		self.setContextMenuPolicy(Qt.CustomContextMenu)
		self.customContextMenuRequested.connect(self._contextMenuRequested)

	def _setupUI(self):
		self.picLabel: QLabel = QLabel()
		self.picLabel.setScaledContents(True)
		self.picLabel.setCursor(QCursor(Qt.PointingHandCursor))
		self.UpdateC4DIconImageSource()

		versLabel: QLabel = QLabel(self.c4d.GetVersionString())
		versLabel.setFont(QFont(APPLICATION_FONT_FAMILY, 12))
		versLabel.setAlignment(Qt.AlignHCenter)

		folderLabel: QLabel = QLabel(self.c4d.GetNameFolderRoot()[:20])
		folderLabel.setAlignment(Qt.AlignHCenter)
		# folderLabel.setWordWrap(True)
		folderLabel.setFont(QFont(APPLICATION_FONT_FAMILY, 10))

		self.tagsWidget: QWidget = self._createTagsSectionWidget()

		layout: QVBoxLayout = QVBoxLayout()
		layout.addWidget(versLabel, alignment=Qt.AlignCenter)
		layout.addWidget(self.picLabel, alignment=Qt.AlignCenter)
		layout.addWidget(folderLabel, alignment=Qt.AlignCenter)
		layout.addWidget(self.tagsWidget, alignment=Qt.AlignCenter)

		self.setLayout(layout)

		picSize: int = int(min(self.width(), self.height()) * 2.)
		self.picLabel.setFixedSize(picSize, picSize)

		self.c4dProcessStatusLabel: QLabel = QLabel(self)
		self.c4dProcessStatusLabel.setFixedSize(16, 16)
		self.c4dProcessStatusLabel.setGeometry(QRect(QPoint(1, 1), self.c4dProcessStatusLabel.size()))
		self.UpdateC4DStatusColor()
	
	def LoadC4DIcon(self) -> QPixmap:
		# Many thanks to Ronald for the icons: https://backstage.maxon.net/topic/3064/cinema-4d-icon-pack
		useRondalds: bool = self.GetPreference('appearance_ronalds-icons')
		c4dIconName: str = ('C4D ' + self.c4d.GetVersionMajor() + '.png') if useRondalds else '_C4D.png'
		c4dIconNameFallback: str = 'C4D Color Purple.png' if useRondalds else '_C4D.png'
		c4dIconPath: str = os.path.join(C4D_ICONS_FOLDER, c4dIconName)
		c4dIconFallbackPath: str = os.path.join(C4D_ICONS_FOLDER, c4dIconNameFallback)
		return QPixmap(c4dIconPath if os.path.isfile(c4dIconPath) else c4dIconFallbackPath)
	
	def GetPreference(self, attr: str):
		return self.parentTilesWidget.GetPreference(attr)

	def _createTagsSectionWidget(self):
		tagsLayout: QHBoxLayout = QHBoxLayout() # TODO: make it work with FlowLayout? # self.tagsLayout: FlowLayout = FlowLayout()
		tagsWidget: QWidget = QWidget()
		tagsWidget.setLayout(tagsLayout)
		tagsDict: dict = self.parentTilesWidget.GetTagBindings() if self.parentTilesWidget else None
		if tagsDict and self.c4d.directory in tagsDict:
			uuids: list[str] = tagsDict[self.c4d.directory]
			for uuid in uuids:
				tag: C4DTag = self.parentTilesWidget.GetTag(uuid)
				if tag is None:
					continue
				tagBubbleWidget: TagBubbleWidget = TagBubbleWidget(tag, None, 5, 3)
				font = tagBubbleWidget.font()
				font.setPixelSize(10)
				tagBubbleWidget.setFont(font)
				tagsLayout.addWidget(tagBubbleWidget)
		return tagsWidget
	
	def _mouseClicked(self, evt: QMouseEvent):
		action: QAction | None = self._getActionForMouseClick(evt.button(), evt.modifiers())
		if action: action.trigger()

	def _getActionForMouseClick(self, button: Qt.MouseButton, modifiers: Qt.KeyboardModifiers):
		if button == Qt.LeftButton:
			if modifiers & Qt.KeyboardModifier.ControlModifier:
				if modifiers & Qt.KeyboardModifier.ShiftModifier: 			# Ctrl+Shift+LClick: open prefs folder
					return self.actionOpenFolderPrefs
				else: 														# Ctrl+LClick: run with console
					return self.actionRunC4DConsole
			elif modifiers & Qt.KeyboardModifier.ShiftModifier: 			# Shift+LClick: open c4d folder
				return self.actionOpenFolder
			else: 															# LClick: run c4d
				return self.actionRunC4D
		if button == Qt.MiddleButton:
			if modifiers & Qt.KeyboardModifier.ControlModifier:
				return self.actionRestartC4D 								# Ctrl+MClick: restart c4d
			elif modifiers & Qt.KeyboardModifier.ShiftModifier:
				return self.actionKillC4D 									# Shift+MClick: kill c4d
			else:
				return self.actionActivateC4D 								# MClick: activate c4d
		return None

	def _runC4D(self, args: list[str] = []):
		# https://forum.qt.io/topic/129701/qprocess-startdetached-but-the-child-process-closes-when-the-parent-exits/6
		if self.GetC4DProcessPIDStatus() > 0 and WinUtils.IsPIDExisting(self.GetC4DProcessPIDStatus()):
			QMessageBox.warning(self, self.c4d.directory, 'This Cinema 4D instance is already running..', QMessageBox.Ok)
			return
		
		self.c4dProcess.setProgram(self.c4d.GetPathExecutable())
		self.c4dProcess.setArguments(args)
		self.c4dProcessArgs = args

		_, processPID = self.c4dProcess.startDetached()
		self.SetC4DProcessPIDStatus(processPID)
	
	def _killC4D(self, silent: bool = False):
		if self.GetC4DProcessPIDStatus() > 0 and WinUtils.IsPIDExisting(self.GetC4DProcessPIDStatus()):
			WinUtils.KillProcessByPID(self.GetC4DProcessPIDStatus())
			self.SetC4DProcessPIDStatus(-2, silent)

	def _restartC4D(self):
		self._killC4D(True) # silent here, to not emit signal twice (getting 'RuntimeError: wrapped C/C++ object of type C4DTile has been deleted' o/w)
		self.c4dProcessRestartTime.start()

	# pidStatus: 0 - not yet started this session, -1 - started but was closed, -2 - started but was killed
	# silent: if True doesn't emit c4dStatusChanged signal
	def SetC4DProcessPIDStatus(self, pidStatus: int, silent: bool = False):
		if c4dCacheInfo := self.GetCacheInfo():
			oldPIDStatus: int = c4dCacheInfo.processStatus
			c4dCacheInfo.processStatus = pidStatus
			if not silent and pidStatus != oldPIDStatus:
				self.c4dStatusChanged.emit(pidStatus)

	def GetC4DProcessPIDStatus(self) -> int:
		if c4dCacheInfo := self.GetCacheInfo():
			return c4dCacheInfo.processStatus
		return 0

	def UpdateC4DStatusColor(self):
		statusColorMap: dict[int, str] = {
			0: '#cccccc', # not yet started, gray
			-2: '#ff0000', # started, but was killed, red
			-1: '#0077ff', # was running, but not there anymore -> blue
			1: '#00ff00', # started, running, green
		}
		c4dPIDStatus: int = self.GetC4DProcessPIDStatus()
		return self.c4dProcessStatusLabel.setStyleSheet(f'background-color: {statusColorMap[min(c4dPIDStatus, 1)]};')
	
	def UpdateC4DIconImageSource(self):
		self.picLabel.setPixmap(self.LoadC4DIcon())
	
	def _activateC4D(self):
		hwnds = WinUtils.getHWNDsForPID(self.GetC4DProcessPIDStatus())
		c4dMainWindowRE = re.compile(f'^Cinema 4D {self.c4d.GetVersionString()} *')
		mainWindowHWNDs = [hwnd for hwnd in hwnds if c4dMainWindowRE.match(WinUtils.getWindowTitleByHandle(hwnd))]
		if len(mainWindowHWNDs) != 1:
			return
		hwnd: int = mainWindowHWNDs[0]
		if WinUtils.isWindowMinimized(hwnd):
			WinUtils.maximizeWindow(hwnd)
		WinUtils.setWindowForeground(hwnd)

	def _setNote(self, text: str):
		ci: C4DCacheInfo = self.GetCacheInfo()
		if ci is None: return
		ci.note = text
		self.setToolTip(self._createTooltipMenuString())

	def _openNoteEditor(self):
		ci: C4DCacheInfo = self.GetCacheInfo()
		dlg: NoteEditorDialog = NoteEditorDialog(f'Edit note for {self.c4d.GetNameFolderRoot()}', ci.note if ci else '', self)
		dlg.setMinimumSize(400, 200)
		if dlg.exec_() == QDialog.Accepted:
			self._setNote(dlg.GetNoteText())

	def _createTooltipMenuString(self):
		ci: C4DCacheInfo = self.GetCacheInfo()
		c4dNote: str = ci.note if ci else ''
		tDt: dt.datetime = GetFolderTimestampCreated(self.c4d.GetPathFolderRoot())
		return f'{self.c4d.GetPathFolderRoot()}'\
			 + f'\nCreated {tDt.strftime("%d/%m/%Y %H:%M")}'\
			+ (f'\nNote: {c4dNote}' if c4dNote else '')
	
	def _addActions(self):
		self.actionRunC4D = QAction('Run C4D')
		self.actionRunC4D.triggered.connect(lambda: self._runC4D())

		self.actionRunC4DConsole = QAction('Run C4D w/console')
		self.actionRunC4DConsole.triggered.connect(lambda: self._runC4D(['g_console=true']))

		self.actionActivateC4D = QAction('Activate C4D') # https://stackoverflow.com/questions/2090464/python-window-activation
		self.actionActivateC4D.triggered.connect(self._activateC4D)

		self.actionKillC4D = QAction('Kill C4D')
		self.actionKillC4D.triggered.connect(self._killC4D)

		self.actionRestartC4D = QAction('Restart C4D')
		self.actionRestartC4D.triggered.connect(self._restartC4D)
		
		self.actionOpenFolder = QAction('Open folder')
		self.actionOpenFolder.triggered.connect(lambda: OpenFolderInDefaultExplorer(self.c4d.GetPathFolderRoot()))
		
		self.actionOpenFolderPrefs = QAction('Open folder prefs')
		self.actionOpenFolderPrefs.triggered.connect(lambda: OpenFolderInDefaultExplorer(self.c4d.GetPathFolderPrefs()))
		self.actionOpenFolderPrefs.setEnabled(bool(self.c4d.GetPathFolderPrefs()))
			
		self.actionEditNote = QAction('Edit note')
		self.actionEditNote.triggered.connect(self._openNoteEditor)

	def _contextMenuRequested(self):
		menu = QtWidgets.QMenu()

		menu.addAction(self.actionRunC4D)
		menu.addAction(self.actionRunC4DConsole)
		menu.addSeparator()
		menu.addAction(self.actionActivateC4D)
		menu.addAction(self.actionRestartC4D)
		menu.addAction(self.actionKillC4D)
		menu.addSeparator()
		menu.addAction(self.actionOpenFolder)
		menu.addAction(self.actionOpenFolderPrefs)
		menu.addSeparator()
		menu.addAction(self.actionEditNote)

		menu.exec_(QtGui.QCursor.pos())

	# def _emitStatusBarSignal(self, modifiers: Qt.KeyboardModifiers | None = None):
	# 	# if not self.picLabel.underMouse(): return

	# 	action: QAction | None = self._getActionForMouseClick(Qt.MouseButton.LeftButton, modifiers if modifiers else Qt.KeyboardModifiers())
	# 	if action is None: return
		
	# 	# self.statusBarTextRequested.emit(action.statusTip())
	# 	self.statusBar.showMessage(action.statusTip(), 0)

	# def mouseMoveEvent(self, evt: QMouseEvent) -> None:
	# 	self._emitStatusBarSignal(modifiers=evt.modifiers())
	# 	return super().mouseMoveEvent(evt)
	
	# def keyPressEvent(self, evt: QKeyEvent) -> None:
	# 	self._emitStatusBarSignal(modifiers=evt.modifiers())
	# 	return super().keyPressEvent(evt)

	# def event(self, evt: QEvent) -> bool:
	# 	if evt.type() == evt.Type.StatusTip:
	# 		print(evt.tip())
	# 		return True
	# 	return super().event(evt)

	def _bindTag(self, uuid: str, placeAsFirst: bool = False):
		c4dCacheInfo: C4DCacheInfo = self.GetCacheInfo() if self.parentTilesWidget else None
		if c4dCacheInfo is None: return
		uuidsList: list[str] = c4dCacheInfo.tagUuids.copy() # TODO: strange bug here, when chaning one list changes tag list for all c4ds
		try:
			foundIdx: int = uuidsList.index(uuid)
			if not placeAsFirst or foundIdx == 0: # nothing else is needed, exiting
				return
			del uuidsList[foundIdx] # found but need to rearrange, deleting existing occurence
		except: # not found, just continuing normally
			pass

		uuidsList.insert(0 if placeAsFirst else len(uuidsList), uuid)
		c4dCacheInfo.tagUuids = uuidsList
		self._rebuildTagsWidget() # need to rebuild tags widget
		
	def _unbindTag(self, uuid: str):
		c4dCacheInfo: C4DCacheInfo = self.GetCacheInfo() if self.parentTilesWidget else None
		if c4dCacheInfo is None: return
		uuidsList: list[str] = c4dCacheInfo.tagUuids.copy() # TODO: strange bug here, when chaning one list changes tag list for all c4ds
		try:
			foundIdx: int = uuidsList.index(uuid)
			del uuidsList[foundIdx]
		except:
			return
		c4dCacheInfo.tagUuids = uuidsList
		self._rebuildTagsWidget() # need to rebuild tags widget
	
	def GetCacheInfo(self) -> C4DCacheInfo | None:
		return self.parentTilesWidget.GetCacheInfo(self.c4d.directory) if self.parentTilesWidget else None

	def _rebuildTagsWidget(self):
		tagsWidgetNew = self._createTagsSectionWidget()
		self.layout().replaceWidget(self.tagsWidget, tagsWidgetNew)
		self.tagsWidget.deleteLater()
		self.tagsWidget = tagsWidgetNew

	def dragEnterEvent(self, evt: QDragEnterEvent):
		if evt.mimeData().hasFormat(C4DTAG_MIMETYPE):
			return evt.accept()
		evt.ignore()

	def dropEvent(self, evt: QDropEvent):
		mimeData: QMimeData = evt.mimeData()
		if not mimeData.hasFormat(C4DTAG_MIMETYPE):
			return evt.ignore()
		tagUuid: str = str(evt.mimeData().data(C4DTAG_MIMETYPE), encoding='utf-8')
		# print(tagUuid)
		if evt.keyboardModifiers() & Qt.ControlModifier: 	# place this tag at first place
			self._bindTag(tagUuid, True)
		elif evt.keyboardModifiers() & Qt.ShiftModifier: 	# remove tag
			self._unbindTag(tagUuid)
		else: 												# append tag at the bottom
			self._bindTag(tagUuid, False)
		# pos, widget = evt.pos(), evt.source()
		evt.accept()

class C4DTilesWidget(QScrollArea):
	CACHE_FILENAME = 'cache.json'
	
	c4dStatusChanged = pyqtSignal(C4DInfo, int)

	def __init__(self, parent: QWidget | None = None) -> None:
		self.mainWindow = parent # TODO: this is bad design!
		super().__init__(parent)

		self.c4dEntries: list[C4DInfo] = list() 				# 
		self.c4dGroups: list[C4DTileGroup] = [C4DTileGroup()] 	# for visual purposes
		self.c4dCacheInfo: dict[str, C4DCacheInfo] = dict() 	# mapping from c4d_directory to a C4DInfoCache

		self.groupLikeWidgets: list[QWidget] = list()

		self.setWidgetResizable(True)

		# This timer checks all running c4d instances to be non-existent anymore, updates c4dtile and emits c4dStatusChanged signal
		self.c4dProcessStatusTimer: QTimer = QTimer()
		self.c4dProcessStatusTimer.setInterval(1000)
		self.c4dProcessStatusTimer.setSingleShot(False)
		self.c4dProcessStatusTimer.setTimerType(Qt.TimerType.PreciseTimer)
		self.c4dProcessStatusTimer.timeout.connect(self._onC4DProcessStatusTimerTimeout)
		self.c4dProcessStatusTimer.start()
	
	def GetC4DEntries(self) -> list[C4DInfo]:
		return self.c4dEntries

	def GetTags(self) -> list[C4DTag]:
		if dlg := self.mainWindow:
			return dlg.GetTags()
		return list()
	
	def GetTag(self, uuid: str) -> C4DTag | None:
		if dlg := self.mainWindow:
			return dlg.GetTag(uuid)
		return None
	
	def GetPreference(self, attr: str):
		return self.mainWindow.GetPreference(attr)
	
	def GetCacheInfo(self, c4dDir: str) -> C4DCacheInfo | None:
		return self.c4dCacheInfo[c4dDir] if c4dDir in self.c4dCacheInfo else None
	
	def GetTagBindings(self) -> dict[str, list[str]]:
		return {c4d: ci.tagUuids for c4d, ci in self.c4dCacheInfo.items()}
	
	def GetGroupsVisibility(self) -> dict[C4DTileGroup, bool]:
		return {self.c4dGroups[idx]: grpWidget.layout().itemAt(0).widget().isVisible() for idx, grpWidget in enumerate(self.groupLikeWidgets) if grpWidget.layout().count()}
	
	def SetGroupsVisibility(self, visibleStates: dict[C4DTileGroup, bool]):
		for idx, groupLikeWidget in enumerate(self.groupLikeWidgets):
			if not isinstance(groupLikeWidget, QGroupBox): continue

			grp: C4DTileGroup = self.c4dGroups[idx]
			if grp not in visibleStates: continue

			groupLikeWidget.setChecked(visibleStates[grp])
			if not groupLikeWidget.layout().count(): continue
			
			innerGroupWidget: QWidget = groupLikeWidget.layout().itemAt(0).widget()
			C4DTilesWidget.SetWidgetVisible(innerGroupWidget, visibleStates[grp])
	
	def ReloadTilesIcons(self):
		groupLikeWidget: QWidget
		for groupLikeWidget in self.groupLikeWidgets:
			if not groupLikeWidget.layout() or not groupLikeWidget.layout().count():
				continue

			innerGroupWidget: QWidget = groupLikeWidget.layout().itemAt(0).widget()
			if not innerGroupWidget or not innerGroupWidget.layout():
				continue

			for idx in range(innerGroupWidget.layout().count()):
				c4dTileWidget: C4DTile = innerGroupWidget.layout().itemAt(idx).widget()
				if not c4dTileWidget:
					continue
				
				c4dTileWidget.UpdateC4DIconImageSource()
	
	@staticmethod
	def SetWidgetVisible(containerWidget: QWidget, setVisible: bool):
		containerWidget.setVisible(setVisible)
	
	def updateTiles(self, c4ds: list[C4DInfo], grouping: list[C4DTileGroup] | None = None):
		self.c4dEntries = c4ds
		if grouping is not None:
			self.c4dGroups = grouping
		if not len(self.c4dGroups):
			self.c4dGroups = [C4DTileGroup()]
		self._rebuildWidget()

	def _rebuildWidget(self):
		if self.widget(): self.widget().deleteLater()

		groupsLayout: QVBoxLayout = QVBoxLayout()
		centralWidget: QWidget = QWidget(self)
		centralWidget.setLayout(groupsLayout)
		centralWidget.setMinimumWidth(100)
		self.setWidget(centralWidget)

		self.groupLikeWidgets.clear()
		# Populate
		for grp in self.c4dGroups:
			innerGroupLayout: FlowLayout = FlowLayout()
			indices = grp.indices
			if not len(indices): indices = [i for i in range(len(self.c4dEntries))]
			for idx in indices:
				c4dinfo: C4DInfo = self.c4dEntries[idx]
				if c4dinfo.directory not in self.c4dCacheInfo:
					self.c4dCacheInfo[c4dinfo.directory] = C4DCacheInfo()
				tileWidget: C4DTile = C4DTile(c4dinfo, self)
				tileWidget.c4dStatusChanged.connect(partial(lambda info, status: self.c4dStatusChanged.emit(info, status), c4dinfo)) # inform main window if c4dtile reported c4d status change
				innerGroupLayout.addWidget(tileWidget)

			grouplikeWidget: QWidget
			
			# 			main widget 							either group or dummy container 				container for hiding content 			c4d tile
			# (QWidget)centralWidget{QVBoxLayout} => (QWidget | QGroupBox)grouplikeLayout{QHBoxLayout} => (QWidget)innerGroupWidget{FlowLayout} => (C4DTile)tileWidget
			innerGroupWidget: QWidget = QWidget()
			innerGroupWidget.setLayout(innerGroupLayout)

			createGroup: bool = len(grp.name)
			if createGroup:
				grouplikeWidget = QGroupBox(grp.name)
				grouplikeWidget.setCheckable(True) # https://stackoverflow.com/questions/55977559/changing-qgroupbox-checkbox-visual-to-an-expander
				grouplikeWidget.clicked.connect(partial(C4DTilesWidget.SetWidgetVisible, innerGroupWidget))
			else:
				grouplikeWidget = QWidget()

			grouplikeLayout: QHBoxLayout = QHBoxLayout()
			grouplikeWidget.setLayout(grouplikeLayout)
			grouplikeLayout.addWidget(innerGroupWidget)

			grouplikeWidget.setFont(QFont(APPLICATION_FONT_FAMILY, 10))
			groupsLayout.addWidget(grouplikeWidget)
			self.groupLikeWidgets.append(grouplikeWidget)
		
		groupsLayout.addStretch()
	
	# on timer tick check if there're any running c4d instance closed, inform mainwindow about that through c4dStatusChanged signal
	def _onC4DProcessStatusTimerTimeout(self):
		for c4dInfo in self.c4dEntries:
			if c4dInfo.directory not in self.c4dCacheInfo:
				continue
			c4dCacheInfo = self.c4dCacheInfo[c4dInfo.directory]
			if c4dCacheInfo.processStatus <= 0 or WinUtils.IsPIDExisting(c4dCacheInfo.processStatus):
				continue
			c4dCacheInfo.processStatus = -1 # c4d instance was closed
			self.c4dStatusChanged.emit(c4dInfo, c4dCacheInfo.processStatus) # TODO: not threadsafe when running on timer callback!!!
	
	def _tagRemoveFromAll(self, tag: C4DTag):
		for c4dCacheInfo in self.c4dCacheInfo.values():
			if tag.uuid in c4dCacheInfo.tagUuids:
				c4dCacheInfo.tagUuids.remove(tag.uuid)
		self._rebuildWidget()
	
	def SaveCache(self):
		saveFilePath: str = self.GetCacheSavePath()

		storeDict: dict = dict()
		storeDict['version'] = C4DL_VERSION
		storeDict['cache']: dict[str, dict] = dict() # mapping of c4ds to their properties

		cache: dict[str, dict] = storeDict['cache']
		# first create new dict for all stored c4ds
		for c4dinfo in self.c4dEntries:
			if c4dinfo.directory not in self.c4dCacheInfo:
				self.c4dCacheInfo[c4dinfo.directory] = C4DCacheInfo()
			cache[c4dinfo.directory] = self.c4dCacheInfo[c4dinfo.directory].ToJSON()

		with open(saveFilePath, 'w') as fp:
			json.dump(storeDict, fp)
	
	def LoadCache(self):
		# TODO: Use QSettings instead? check preferences window as well
		loadFilePath: str = self.GetCacheSavePath()
		if not os.path.isfile(loadFilePath):
			return

		knownC4DPaths: list[str] = [c4dinfo.directory for c4dinfo in self.c4dEntries]
		with open(loadFilePath, 'r') as fp:
			data: dict = json.load(fp)
			if 'version' in data:
				print(f"Loading cache: file version {data['version']}")
			if 'cache' in data:
				cache: dict[str, dict] = data['cache']
				for c4d, c4dDict in cache.items():
					if c4d not in knownC4DPaths:
						print(f'Cache contains entry that is not found anymore! C4D Path: {c4d}')
						continue
					self.c4dCacheInfo[c4d]: C4DCacheInfo = C4DCacheInfo.FromJSON(c4dDict) if 'tagUuids' in c4dDict else C4DCacheInfo()
		self._rebuildWidget()

	
	@staticmethod
	def GetCacheSavePath():
		prefsFolderPath: str = GetPrefsFolderPath()
		return os.path.join(prefsFolderPath, C4DTilesWidget.CACHE_FILENAME)