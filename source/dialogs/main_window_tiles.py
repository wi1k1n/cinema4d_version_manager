import sys, os, typing, datetime as dt
from subprocess import Popen, PIPE
from PyQt5 import QtCore, QtGui

from PyQt5.QtCore import QObject, Qt, QEvent, pyqtSignal, QProcess, QRect, QPoint
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
	QProxyStyle
)

# import qrc_resources
from dialogs.preferences import PreferencesWindow
from dialogs.about import AboutWindow
from dialogs.tags import TagsWindow, C4DTag
from utils import *
from gui_utils import *

class C4DTileGroup:
	def __init__(self, indices: list[int] = list(), name: str = '') -> None:
		self.indices = indices
		self.name = name

# TODO: here for now, please remove once not needed!
class C4DTile2(QWidget):
	def __init__(self, c4d: C4DInfo, parent: QWidget | None = None) -> None:
		super().__init__(parent)

		self.setFixedSize(100, 100)
		self.pixMap: QPixmap = QPixmap(os.path.join(C4D_ICONS_FOLDER, 'Color Purple.png'))
		

	def paintEvent(self, evt: QPaintEvent) -> None:
		p: QPainter = QPainter(self)

		p.fillRect(self.rect(), QBrush(Qt.red, Qt.Dense5Pattern))

		p.drawPixmap(QRect(0, 0, 60, 60), self.pixMap)

		p.setFont(QFont('Comic', 18))
		p.drawText(self.rect(), Qt.AlignLeft | Qt.AlignVCenter, 'Hello world!')

		return super().paintEvent(evt)

class C4DTile(QFrame):
	# https://forum.qt.io/topic/90403/show-tooltip-immediatly/6
	class C4DTileProxyStyle(QProxyStyle):
		def styleHint(self, hint: QStyle.StyleHint, option: QStyleOption | None = None, widget: QWidget | None = None, returnData: QStyleHintReturn | None = None) -> int:
			if hint == QStyle.SH_ToolTip_WakeUpDelay:
				return 0
			return super().styleHint(hint, option, widget, returnData)

	def __init__(self, c4d: C4DInfo, parent: QWidget | None = None) -> None:
		self.parentTilesWidget = parent
		super().__init__(parent)

		self.c4d: C4DInfo = c4d

		self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
		self.setLineWidth(1)
		# self.setFixedSize(100, 100)
		self.setAcceptDrops(True)
		# self.setMouseTracking(True)
		self.setStyle(C4DTile.C4DTileProxyStyle())

		self._setupUI()
		self._addActions()
		
		self.picLabel.mousePressEvent = self._mouseClicked

		self.setContextMenuPolicy(Qt.CustomContextMenu)
		self.customContextMenuRequested.connect(self._contextMenuRequested)

	def _setupUI(self):
		# Many thanks to Ronald for the icons: https://backstage.maxon.net/topic/3064/cinema-4d-icon-pack
		c4dIconName: str = 'C4D ' + self.c4d.GetVersionMajor() + '.png'
		c4dIconPath: str = os.path.join(C4D_ICONS_FOLDER, c4dIconName)
		pic = QPixmap(c4dIconPath if os.path.isfile(c4dIconPath) else os.path.join(C4D_ICONS_FOLDER, 'Color Purple.png'))

		self.picLabel: QLabel = QLabel()
		self.picLabel.setPixmap(pic)
		self.picLabel.setScaledContents(True)
		self.picLabel.setCursor(QCursor(Qt.PointingHandCursor))

		versLabel: QLabel = QLabel(self.c4d.GetVersionString())
		versLabel.setFont(QFont('SblHebrew', 12))
		versLabel.setAlignment(Qt.AlignHCenter)

		folderLabel: QLabel = QLabel(self.c4d.GetNameFolderRoot()[:20])
		folderLabel.setAlignment(Qt.AlignHCenter)
		# folderLabel.setWordWrap(True)
		folderLabel.setFont(QFont('SblHebrew', 10))

		self.tagsWidget: QWidget = self._createTagsSectionWidget()

		layout: QVBoxLayout = QVBoxLayout()
		layout.addWidget(versLabel, alignment=Qt.AlignCenter)
		layout.addWidget(self.picLabel, alignment=Qt.AlignCenter)
		layout.addWidget(folderLabel, alignment=Qt.AlignCenter)
		layout.addWidget(self.tagsWidget, alignment=Qt.AlignCenter)

		self.setLayout(layout)

		picSize: int = int(min(self.width(), self.height()) * 3.)
		self.picLabel.setFixedSize(picSize, picSize)

		self.setToolTip(self._createTooltipMenuString())

	def _createTagsSectionWidget(self):
		tagsLayout: QHBoxLayout = QHBoxLayout() # TODO: make it work with FlowLayout? # self.tagsLayout: FlowLayout = FlowLayout()
		tagsWidget: QWidget = QWidget()
		tagsWidget.setLayout(tagsLayout)
		tagsDict: dict = self.parentTilesWidget.c4dTags if self.parentTilesWidget else None
		if tagsDict and self.c4d.directory in tagsDict:
			uuids: list[str] = tagsDict[self.c4d.directory]
			for uuid in uuids:
				tag: C4DTag = self.parentTilesWidget.GetTag(uuid)
				# print(tag)
				tagBubbleWidget: BubbleWidget = BubbleWidget(tag.name, tag.color, 5, 3)
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
				if modifiers & Qt.KeyboardModifier.ShiftModifier: 			# Ctrl+Shift+Click: open prefs folder
					return self.actionOpenFolderPrefs
				else: 														# Ctrl+Click: run with console
					return self.actionRunC4DConsole
			elif modifiers & Qt.KeyboardModifier.ShiftModifier: 			# Shift+Click: open c4d folder
				return self.actionOpenFolder
			else: 															# Click: run c4d
				return self.actionRunC4D
		return None

	def _runC4D(self, args: list[str] = []):
		# https://forum.qt.io/topic/129701/qprocess-startdetached-but-the-child-process-closes-when-the-parent-exits/6
		self.p: QProcess = QProcess()
		print(self.p.startDetached(self.c4d.GetPathExecutable(), args))
		self.p.setStandardErrorFile(QProcess.nullDevice())
		self.p.setStandardInputFile(QProcess.nullDevice())
		self.p.setStandardOutputFile(QProcess.nullDevice())
		self.p.setProcessState(QProcess.NotRunning)

	def _createTooltipMenuString(self):
		tDt: dt.datetime = GetFolderTimestampCreated(self.c4d.GetPathFolderRoot())
		return f'{self.c4d.GetPathFolderRoot()}'\
				f'\nCreated {tDt.strftime("%d/%m/%Y %H:%M")}'
	
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

	def _bindTag(self, uuid: str):
		tagsDict: dict = self.parentTilesWidget.c4dTags if self.parentTilesWidget else None
		if not tagsDict or self.c4d.directory not in tagsDict:
			return
		if uuid in tagsDict[self.c4d.directory]:
			return
		tagsDict[self.c4d.directory].append(uuid)

		# we need to rebuild tags widget
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
		print(tagUuid)
		self._bindTag(tagUuid)
		# pos, widget = evt.pos(), evt.source()
		# print(pos, widget)
		evt.accept()

class C4DTilesWidget(QScrollArea):
	def __init__(self, parent: QWidget | None = None) -> None:
		self.mainWindow = parent
		super().__init__(parent)

		self.c4dEntries: list[C4DInfo] = list()
		self.c4dTags: dict[str, list[str]] = dict() # mapping from c4d_directory to a list of uuids to the tags

		self.setWidgetResizable(True)
	
	def GetTags(self) -> list[C4DTag]:
		if dlg := self.mainWindow:
			return dlg.GetTags()
		return list()
	def GetTag(self, uuid: str) -> C4DTag | None:
		if dlg := self.mainWindow:
			return dlg.GetTag(uuid)
		return None
	
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
				c4dinfo: C4DInfo = self.c4dEntries[idx]
				# self.c4dTags[c4dinfo.directory] = [t.uuid for t in self.GetTags()]
				self.c4dTags[c4dinfo.directory] = list()
				tileWidget: C4DTile = C4DTile(c4dinfo, self)
				flowLayout.addWidget(tileWidget)

			createGroup: bool = len(grp.name)
			curWidget: QWidget
			if createGroup:
				curWidget = QGroupBox(grp.name)
			else:
				curWidget = QWidget()
			curWidget.setLayout(flowLayout)
			groupsLayout.addWidget(curWidget)
		
		groupsLayout.addStretch()

		print(self.GetTags())