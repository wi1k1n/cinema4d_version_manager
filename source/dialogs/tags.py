import os, json, typing
from functools import partial

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, QUrl, QRect, QPoint
from PyQt5.QtGui import QFont, QDesktopServices, QMouseEvent, QShowEvent, QPaintEvent, QPainter, QColor, QPalette
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
	QDialogButtonBox
)

from version import *
from gui_utils import *

class C4DTag:
	def __init__(self, name: str) -> None:
		self.name: str = name

class TagWidget(DraggableBubbleWidget):
	def __init__(self, tag: C4DTag):
		super().__init__(tag.name)
		
		self.tag: C4DTag = tag
		# self.mousePressEvent = self._onMousePress
	
	def GetTag(self) -> C4DTag:
		return self.tag
	
	# def _onMousePress(self, evt: QMouseEvent):
	# 	print(self)
class ColorPickerWidget(QWidget):
	def __init__(self, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self.originalColor = self.palette().color(self.backgroundRole())
		self.ResetColor()
		self.mousePressEvent = self._openColorSelector
	
	def GetColor(self) -> QColor:
		return self.color
	
	def ResetColor(self):
		self.SetColor(self.originalColor)

	def SetColor(self, color: QColor):
		self.color = color

	def _openColorSelector(self, evt):
		dlg: QColorDialog = QColorDialog(self.color)
		dlg.exec_()
		self.SetColor(dlg.currentColor())

	def paintEvent(self, evt: QPaintEvent) -> None:
		qp: QPainter = QPainter(self)
		qp.setBrush(self.color)
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
		if tag: # editing existing tag
			self.setWindowTitle("Edit tag")
			self.tag = tag
		else:
			self.setWindowTitle('Create tag')
			self.colorWidget.ResetColor()
			self.tag = C4DTag('New tag')

		self.lineEditName.setText(self.tag.name)
	
	def GetTag(self) -> C4DTag:
		return self.tag
	
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

		self.setWindowTitle("Tags")
		self.setWindowFlags(self.windowFlags() & Qt.WindowCloseButtonHint)
		self.resize(400, 400)

		mainArea = QtWidgets.QScrollArea(self)
		mainArea.setWidgetResizable(True)

		widget = QtWidgets.QWidget(mainArea)
		widget.setMinimumWidth(50)

		self.tagWidgets: list[TagWidget] = [TagWidget(t) for t in tags]
		layout = FlowLayout(widget)
		self.words = []
		for tagWidget in self.tagWidgets:
			tagWidget.setFont(QtGui.QFont('SblHebrew', 18))
			tagWidget.setFixedWidth(tagWidget.sizeHint().width())
			tagWidget.mouseDoubleClickEvent = partial(self._openManageTagWindowExisting, tagWidget)
			layout.addWidget(tagWidget)

		mainArea.setWidget(widget)
		self.setWidget(mainArea)

		self.mouseDoubleClickEvent = self._openManageTagWindowNew
		self.manageTagWindow.accepted.connect(self._onManageTagAccepted)
	
	def _onManageTagAccepted(self):
		tag: C4DTag = self.manageTagWindow.GetTag()
		if tag in [t.GetTag() for t in self.tagWidgets]:
			print('accepted:', tag.name)
		else:
			print('accepted: was new')
	
	def _openManageTagWindowExisting(self, tagWidget: TagWidget, evt: QMouseEvent):
		self.manageTagWindow.SetTag(tagWidget.GetTag())
		self._restoreManageTagWindow()

	def _openManageTagWindowNew(self, evt: QMouseEvent):
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