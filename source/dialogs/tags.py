import os, json, typing, json
from functools import partial

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, QUrl, QRect, QPoint, QTimer, QSize, pyqtSignal, QByteArray
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
from utils import *

class C4DTag:
	def __init__(self, name: str, uuid: str = '', color: QColor | None = None) -> None:
		self.uuid: str = uuid if uuid else GenerateUUID()
		self.name: str = name
		self.color: QColor | None = color
	
	@staticmethod
	def FromJSON(jsonStr: dict):
		name: str = jsonStr['name'] if 'name' in jsonStr else ''
		color: QColor | None = QColor(jsonStr['color']) if 'color' in jsonStr and jsonStr['color'] is not None else None
		uuid: str = jsonStr['uuid'] if 'uuid' in jsonStr else ''
		if not name or not uuid:
			print(f'ERROR Loading C4DTag: {name=} | {uuid=}')
		return C4DTag(name, uuid, color)

	def ToJSON(self) -> dict:
		return {
			'uuid': self.uuid,
			'name': self.name,
			'color': self.color.name() if self.color else None,
		}

class TagWidget(BubbleWidget):
	tagEditRequestedSignal = pyqtSignal()
	tagRemoveRequestedSignal = pyqtSignal()
	tagMoveRequestedSignal = pyqtSignal(int)
	def __init__(self, tag: C4DTag):
		super().__init__(tag.name, tag.color)
		
		self.setFont(QtGui.QFont(APPLICATION_FONT_FAMILY, 18))
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
	
	def GetDragMimeData(self, evt: QMouseEvent):
		mimeData: QMimeData = QMimeData()
		mimeData.setData(C4DTAG_MIMETYPE, QByteArray(self.tag.uuid.encode()))
		return mimeData

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
		
		self.tagUUID: str = tag.uuid if tag else ''
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
		return C4DTag(self.lineEditName.text(), self.tagUUID, self.colorWidget.GetColor())
	
	def IsEditing(self) -> bool:
		return self.isEditing

	def _onAccepted(self):
		self.accept()
		
	def _onRejected(self):
		self.close()

	def showEvent(self, evt: QShowEvent) -> None:
		self.setFixedSize(self.size())
		return evt.accept()

class TagsWindow(QDockWidget):
	TAGS_FILENAME = 'tags.json'

	tagEditedSignal = pyqtSignal(C4DTag)
	tagRemovedSignal = pyqtSignal(C4DTag)

	def __init__(self, parent=None):
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
		self.LoadTags()
		# for tag in tags:
		# 	self._addTag(tag)

		mainArea.setWidget(widget)
		self.setWidget(mainArea)

		self.mouseDoubleClickEvent = lambda evt: self._openManageTagWindowNew()
		self.manageTagWindow.accepted.connect(self._onManageTagAccepted)

		# Actions
		self.actionCreateNewTag = QAction('Create new', self)
		self.actionCreateNewTag.triggered.connect(self._openManageTagWindowNew)
		
		self.addAction(self.actionCreateNewTag)
		self.setContextMenuPolicy(Qt.ActionsContextMenu)
	
	def LoadTags(self):
		# TODO: Use QSettings instead? check preferences window as well
		tagsFilePath: str = self.GetTagsSavePath()
		if not os.path.isfile(tagsFilePath):
			return

		with open(tagsFilePath, 'r') as fp:
			data: dict = json.load(fp)
			if 'version' in data:
				print(f"Loading tags: file version {data['version']}")
			if 'tags' in data:
				tags: list = data['tags']
				for t in tags:
					self._addTag(C4DTag.FromJSON(t))

	def SaveTags(self):
		tagsFilePath: str = self.GetTagsSavePath()

		storeDict: dict = dict()
		storeDict['version'] = C4DL_VERSION
		storeDict['tags'] = list()

		for t in self._getTags():
			storeDict['tags'].append(t.ToJSON())
		
		with open(tagsFilePath, 'w') as fp:
			json.dump(storeDict, fp)
	
	def _addTag(self, tag: C4DTag):
		tagWidget: TagWidget = TagWidget(tag)
		tagWidget.mouseDoubleClickEvent = partial(lambda tw, evt: self._openManageTagWindowExisting(tw), tagWidget)
		tagWidget.tagEditRequestedSignal.connect(partial(self._openManageTagWindowExisting, tagWidget))
		tagWidget.tagRemoveRequestedSignal.connect(partial(self._removeTag, tagWidget.GetTag()))
		tagWidget.tagMoveRequestedSignal.connect(partial(self._moveTag, tagWidget.GetTag()))
		self.tagsFlowLayout.addWidget(tagWidget)
		self.tagWidgets.append(tagWidget)
	
	def _getTags(self) -> list[C4DTag]:
		return [tW.GetTag() for tW in self.tagWidgets]
	def _getTag(self, uuid: str) -> C4DTag | None:
		foundTags: list[C4DTag] = [t for t in self._getTags() if t.uuid == uuid]
		return foundTags[0] if len(foundTags) else None
	
	def _findTagIndex(self, tag: C4DTag):
		for idx, t in enumerate(self._getTags()):
			if t.uuid == tag.uuid: # TODO: proper equality test!
				return idx
		return -1
		
	def _removeTag(self, tag: C4DTag): # TODO: sometimes gives error, likely due to poor C4DTag equality test
		tagIdx: int = self._findTagIndex(tag)
		if tagIdx < 0: return print('Doesn\'t exist!')
		self.tagWidgets[tagIdx].deleteLater()
		del self.tagWidgets[tagIdx]
		self.tagRemovedSignal.emit(tag)
		
	def _moveTag(self, tag: C4DTag, dir: int):
		tagIdx: int = self._findTagIndex(tag)
		if tagIdx < 0: return print('Doesn\'t exist!')
		if tagIdx == 0 and dir < 0 or tagIdx == len(self.tagWidgets) - 1 and dir > 0:
			return
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
			tagNew.uuid = tag.uuid # preserve uuid to stay consistent
			self.tagWidgets[tagIdx].SetTag(tagNew)
			self.tagEditedSignal.emit(tagNew)
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
		
	@staticmethod
	def GetTagsSavePath():
		prefsFolderPath: str = GetPrefsFolderPath()
		return os.path.join(prefsFolderPath, TagsWindow.TAGS_FILENAME)