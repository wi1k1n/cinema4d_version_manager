import os, json, typing
from functools import partial

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, QUrl, QRect, QPoint, QTimer, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QDesktopServices, QMouseEvent, QShowEvent, QPaintEvent, QPainter, QColor, QPalette, QPen
from PyQt5.QtWidgets import (
	QLabel,
	QMainWindow,
	QDockWidget,
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
	QColorDialog,
	QFormLayout,
	QLineEdit,
	QDialogButtonBox,
	QSizePolicy,
	QAction,
	QLayoutItem
)

from version import *
from gui_utils import *

class C4DTag:
	def __init__(self, name: str, color: QColor | None = None) -> None:
		self.name: str = name
		self.color: QColor | None = color

# https://stackoverflow.com/a/18069897
class BubbleWidget(DraggableQLabel):
	def __init__(self, text, bgColor: QColor | None = None, rounding: float = 20, margin: int = 7):
		super(DraggableQLabel, self).__init__(text)
		self.rounding: float = rounding
		self.roundingMargin: int = margin
		self.bgColor: QColor | None = bgColor

		# self.mouseLeaveTimer: QTimer = QTimer(self, interval=50, timeout=self._mouseLeaveTimerCallback)

		self.setContentsMargins(margin, margin, margin, margin)
		self.setAlignment(Qt.AlignCenter)
		self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
		
		# self.setMouseTracking(True)
	
	# def _mouseLeaveTimerCallback(self):
	# 	self.mouseLeaveTimer.stop()
	# 	self.update()

	# def mouseMoveEvent(self, e: QMouseEvent):
	# 	self.mouseLeaveTimer.start()
	# 	self.update()
	# 	return super().mouseMoveEvent(e)

	def SetColor(self, bgColor: QColor | None):
		self.bgColor = bgColor
		self.update()
	
	def SetText(self, txt: str):
		self.setText(txt)
		self.setFixedSize(1, 1) # doesn't work without manually shrinking it first
		self.setFixedSize(self.sizeHint() + QSize(self.roundingMargin, self.roundingMargin) * 2)

	def paintEvent(self, evt: QPaintEvent):
		p: QPainter = QPainter(self)
		
		penWidth: int = 1 # 2 if self.underMouse() else 1
		p.setPen(QPen(Qt.black, penWidth))
		if self.bgColor is not None:
			p.setBrush(self.bgColor)
		
		p.setRenderHint(QPainter.Antialiasing, True)
		p.drawRoundedRect(penWidth, penWidth, self.width() - penWidth * 2, self.height() - penWidth * 2, self.rounding, self.rounding)
		
		super(DraggableQLabel, self).paintEvent(evt)

class TagWidget(BubbleWidget):
	tagEditRequestedSignal = pyqtSignal()
	tagRemoveRequestedSignal = pyqtSignal()
	tagMoveRequestedSignal = pyqtSignal(int)
	def __init__(self, tag: C4DTag):
		super().__init__(tag.name, tag.color)
		
		self.setFont(QtGui.QFont('SblHebrew', 18))
		self.SetTag(tag)
		# self.mousePressEvent = self._onMousePress
		
		# Actions
		self.actionEdit: QAction = QAction('Edit', self)
		self.actionEdit.triggered.connect(self._onEditAction)
		self.actionMoveBack: QAction = QAction('Move back', self)
		self.actionMoveBack.triggered.connect(self._onMoveBackAction)
		self.actionMoveForward: QAction = QAction('Move forward', self)
		self.actionMoveForward.triggered.connect(self._onMoveForwardAction)
		self.actionRemove: QAction = QAction('Remove', self)
		self.actionRemove.triggered.connect(self._onRemoveAction)
		
		def createActionSeparator(self):
			separator: QAction = QAction(self)
			separator.setSeparator(True)
			return separator
		self.addAction(self.actionEdit)
		self.addAction(createActionSeparator(self))
		self.addAction(self.actionMoveBack)
		self.addAction(self.actionMoveForward)
		self.addAction(createActionSeparator(self))
		self.addAction(self.actionRemove)

		self.setContextMenuPolicy(Qt.ActionsContextMenu)
	
	def GetTag(self) -> C4DTag:
		return self.tag
	
	def SetTag(self, tag: C4DTag):
		self.tag: C4DTag = tag
		self.SetText(tag.name)
		self.SetColor(tag.color)

	def _onMoveBackAction(self):
		self.tagMoveRequestedSignal.emit(-1)
	def _onMoveForwardAction(self):
		self.tagMoveRequestedSignal.emit(1)
	def _onEditAction(self):
		self.tagEditRequestedSignal.emit()
	def _onRemoveAction(self):
		self.tagRemoveRequestedSignal.emit()
	
	# def _onMousePress(self, evt: QMouseEvent):
	# 	print(self)

class ColorPickerWidget(QWidget):
	def __init__(self, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self.originalColor = self.palette().color(self.backgroundRole())
		self.selectedColor = self.originalColor
		self.mousePressEvent = self._openColorSelector
	
	def GetColor(self) -> QColor:
		return self.selectedColor
	
	def ResetColor(self):
		self.SetColor(self.originalColor)

	def SetColor(self, color: QColor):
		self.selectedColor = color

	def _openColorSelector(self, evt):
		dlg: QColorDialog = QColorDialog(self.selectedColor)
		dlg.exec_()
		self.SetColor(dlg.currentColor())

	def paintEvent(self, evt: QPaintEvent) -> None:
		qp: QPainter = QPainter(self)
		qp.setBrush(self.selectedColor)
		qp.drawRect(QRect(QPoint(), self.size()))
		return super().paintEvent(evt)
		
class ManageTagDialog(QDialog):
	def __init__(self, parent: QWidget | None = None, tag: C4DTag | None = None) -> None:
		super().__init__(parent)
		
		self.lineEditName: QLineEdit = QLineEdit()
		self.colorWidget: ColorPickerWidget = ColorPickerWidget()
		buttons: QDialogButtonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
		buttons.accepted.connect(self._onAccepted)
		buttons.rejected.connect(self._onRejected)

		formLayout = QFormLayout()
		formLayout.addRow(self.tr('&Name:'), self.lineEditName)
		formLayout.addRow(self.tr('&Color:'), self.colorWidget)

		mainWidget: QWidget = QWidget()
		mainWidget.setLayout(formLayout)

		mainLayout: QVBoxLayout = QVBoxLayout()
		mainLayout.addWidget(mainWidget)
		mainLayout.addWidget(buttons)

		self.setLayout(mainLayout)

		self.SetTag(tag)
	
	def SetTag(self, tag: C4DTag = None):
		self.isEditing: bool = tag is not None
		self.colorWidget.ResetColor()
		if tag: # editing existing tag
			self.setWindowTitle("Edit tag")
			if tag.color:
				self.colorWidget.SetColor(tag.color)
			self.tag = tag
		else:
			self.setWindowTitle('Create tag')
			self.tag = C4DTag('New tag')

		self.lineEditName.setText(self.tag.name)
	
	def GetTag(self) -> C4DTag:
		return self.tag
	
	def GetTagEdited(self) -> C4DTag:
		return C4DTag(self.lineEditName.text(), self.colorWidget.GetColor())
	
	def IsEditing(self) -> bool:
		return self.isEditing

	def _onAccepted(self):
		# print('Accepted')
		self.accept()
		
	def _onRejected(self):
		self.close()

	def showEvent(self, evt: QShowEvent) -> None:
		self.setFixedSize(self.size())
		return evt.accept()

class TagsWindow(QDockWidget):
	def __init__(self, parent=None, tags: list[C4DTag] = list()):
		super().__init__(parent)

		self.manageTagWindow: ManageTagDialog = ManageTagDialog()
		self.tagWidgets: list[TagWidget] = list()

		self.setWindowTitle("Tags")
		self.setWindowFlags(self.windowFlags() & Qt.WindowCloseButtonHint)
		self.resize(400, 400)

		mainArea = QtWidgets.QScrollArea(self)
		mainArea.setWidgetResizable(True)

		widget = QtWidgets.QWidget(mainArea)
		widget.setMinimumWidth(20)

		self.tagsFlowLayout = FlowLayout(widget)
		for tag in tags:
			self._addTag(tag)

		mainArea.setWidget(widget)
		self.setWidget(mainArea)

		self.mouseDoubleClickEvent = lambda evt: self._openManageTagWindowNew()
		self.manageTagWindow.accepted.connect(self._onManageTagAccepted)

		# Actions
		self.actionCreateNewTag = QAction('Create new', self)
		self.actionCreateNewTag.triggered.connect(self._openManageTagWindowNew)
		
		self.addAction(self.actionCreateNewTag)
		self.setContextMenuPolicy(Qt.ActionsContextMenu)
	
	def _addTag(self, tag: C4DTag):
		tagWidget: TagWidget = TagWidget(tag)
		tagWidget.mouseDoubleClickEvent = partial(lambda tw, evt: self._openManageTagWindowExisting(tw), tagWidget)
		tagWidget.tagEditRequestedSignal.connect(partial(self._openManageTagWindowExisting, tagWidget))
		tagWidget.tagRemoveRequestedSignal.connect(partial(self._removeTag, tagWidget.GetTag()))
		tagWidget.tagMoveRequestedSignal.connect(partial(self._moveTag, tagWidget.GetTag()))
		self.tagsFlowLayout.addWidget(tagWidget)
		self.tagWidgets.append(tagWidget)
	
	def _findTagIndex(self, tag: C4DTag):
		for idx, tagWidget in enumerate(self.tagWidgets):
			if tagWidget.GetTag() == tag: # TODO: proper equality test!
				return idx
		return -1
		
	def _removeTag(self, tag: C4DTag): # TODO: sometimes gives error, likely due to poor C4DTag equality test
		tagIdx: int = self._findTagIndex(tag)
		if tagIdx < 0: return print('Doesn\'t exist!')
		print('remove:', tag.name)
		self.tagWidgets[tagIdx].deleteLater()
		del self.tagWidgets[tagIdx]
		
	def _moveTag(self, tag: C4DTag, dir: int):
		tagIdx: int = self._findTagIndex(tag)
		if tagIdx < 0: return print('Doesn\'t exist!')
		if tagIdx == 0 and dir < 0 or tagIdx == len(self.tagWidgets) - 1 and dir > 0:
			return
		print('move tag', tag.name, 'forward' if dir > 0 else 'back')
		items: list[QLayoutItem] = [self.tagsFlowLayout.takeAt(0) for i in range(self.tagsFlowLayout.count())]
		items[tagIdx], items[tagIdx + dir] = items[tagIdx + dir], items[tagIdx]
		for item in items:
			self.tagsFlowLayout.addItem(item)
		self.tagWidgets[tagIdx], self.tagWidgets[tagIdx + dir] = self.tagWidgets[tagIdx + dir], self.tagWidgets[tagIdx]
		self.tagsFlowLayout.update()

	def _onManageTagAccepted(self):			
		tag: C4DTag = self.manageTagWindow.GetTag()
		tagNew: C4DTag = self.manageTagWindow.GetTagEdited()
		tagIdx: int = self._findTagIndex(tag)
		if tagIdx >= 0: # found previous tag
			tagWidget: TagWidget = self.layout().itemAt(tagIdx).widget()
			tagWidget.SetTag(tagNew)
			return
		tagNewIdx: int = self._findTagIndex(tagNew)
		if tagNewIdx >= 0: return print('Already exists!!!')
		self._addTag(tagNew)
	
	def _openManageTagWindowExisting(self, tagWidget: TagWidget):
		self.manageTagWindow.SetTag(tagWidget.GetTag())
		self._restoreManageTagWindow()
	
	def _openManageTagWindowNew(self):
		if self.manageTagWindow.isHidden() or self.manageTagWindow.IsEditing():
			self.manageTagWindow.SetTag()
		self._restoreManageTagWindow()
	
	def _restoreManageTagWindow(self):
		self.manageTagWindow.show()
		self.manageTagWindow.activateWindow()

	def closeEvent(self, event):
		if self.manageTagWindow:
			self.manageTagWindow.close()
		event.accept()