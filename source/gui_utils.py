import typing

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import (
    Qt, QMimeData, QUrl, QRect, QPoint, QTimer, QSize, pyqtSignal, QRectF
)
from PyQt5.QtGui import (
    QFont, QDrag, QPixmap, QDesktopServices, QMouseEvent, QShowEvent, QPaintEvent,
	QPainter, QColor, QPalette, QPen, QPainterPath, QRegion, QCursor
)
from PyQt5.QtWidgets import (
	QLabel, QMainWindow, QDockWidget, QDialog, QHBoxLayout, QListWidget, QWidget,
	QVBoxLayout, QPushButton, QListWidgetItem, QStackedWidget, QFileDialog,
	QLayout, QAbstractItemView, QColorDialog, QFormLayout, QLineEdit,
	QDialogButtonBox, QSizePolicy, QAction, QLayoutItem, QApplication
)

def GetApplication() -> QApplication:
	if app := QtWidgets.QApplication.instance():
		return app
	return QtWidgets.QApplication([])

# FlowLayout implementation is stolen from: https://stackoverflow.com/a/41643802/5765191
class FlowLayout(QtWidgets.QLayout):
	def __init__(self, parent=None, margin=-1, hspacing=-1, vspacing=-1):
		super(FlowLayout, self).__init__(parent)
		self._hspacing = hspacing
		self._vspacing = vspacing
		self._items = []
		self.setContentsMargins(margin, margin, margin, margin)

	def __del__(self):
		del self._items[:]

	def addItem(self, item):
		self._items.append(item)

	def horizontalSpacing(self):
		if self._hspacing >= 0:
			return self._hspacing
		else:
			return self.smartSpacing(
				QtWidgets.QStyle.PM_LayoutHorizontalSpacing)

	def verticalSpacing(self):
		if self._vspacing >= 0:
			return self._vspacing
		else:
			return self.smartSpacing(
				QtWidgets.QStyle.PM_LayoutVerticalSpacing)

	def count(self):
		return len(self._items)

	def itemAt(self, index):
		if 0 <= index < len(self._items):
			return self._items[index]

	def takeAt(self, index):
		if 0 <= index < len(self._items):
			return self._items.pop(index)

	def expandingDirections(self):
		return QtCore.Qt.Orientations(0)

	def hasHeightForWidth(self):
		return True

	def heightForWidth(self, width):
		return self.doLayout(QtCore.QRect(0, 0, width, 0), True)

	def setGeometry(self, rect):
		super(FlowLayout, self).setGeometry(rect)
		self.doLayout(rect, False)

	def sizeHint(self):
		return self.minimumSize()

	def minimumSize(self):
		size = QtCore.QSize()
		for item in self._items:
			size = size.expandedTo(item.minimumSize())
		left, top, right, bottom = self.getContentsMargins()
		size += QtCore.QSize(left + right, top + bottom)
		return size

	def doLayout(self, rect, testonly):
		left, top, right, bottom = self.getContentsMargins()
		effective = rect.adjusted(+left, +top, -right, -bottom)
		x = effective.x()
		y = effective.y()
		lineheight = 0
		for item in self._items:
			widget = item.widget()
			hspace = self.horizontalSpacing()
			if hspace == -1:
				hspace = widget.style().layoutSpacing(
					QtWidgets.QSizePolicy.PushButton,
					QtWidgets.QSizePolicy.PushButton, QtCore.Qt.Horizontal)
			vspace = self.verticalSpacing()
			if vspace == -1:
				vspace = widget.style().layoutSpacing(
					QtWidgets.QSizePolicy.PushButton,
					QtWidgets.QSizePolicy.PushButton, QtCore.Qt.Vertical)
			nextX = x + item.sizeHint().width() + hspace
			if nextX - hspace > effective.right() and lineheight > 0:
				x = effective.x()
				y = y + lineheight + vspace
				nextX = x + item.sizeHint().width() + hspace
				lineheight = 0
			if not testonly:
				item.setGeometry(
					QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))
			x = nextX
			lineheight = max(lineheight, item.sizeHint().height())
		return y + lineheight - rect.y() + bottom

	def smartSpacing(self, pm):
		parent = self.parent()
		if parent is None:
			return -1
		elif parent.isWidgetType():
			return parent.style().pixelMetric(pm, None, parent)
		else:
			return parent.spacing()

# # https://stackoverflow.com/a/52617714
# class CollapsibleBox(QtWidgets.QWidget):
# 	def __init__(self, title="", parent=None):
# 		super(CollapsibleBox, self).__init__(parent)

# 		self.toggle_button = QtWidgets.QToolButton(
# 			text=title, checkable=True, checked=False
# 		)
# 		self.toggle_button.setStyleSheet("QToolButton { border: none; }")
# 		self.toggle_button.setToolButtonStyle(
# 			QtCore.Qt.ToolButtonTextBesideIcon
# 		)
# 		self.toggle_button.setArrowType(QtCore.Qt.RightArrow)
# 		self.toggle_button.pressed.connect(self.on_pressed)

# 		self.toggle_animation = QtCore.QParallelAnimationGroup(self)

# 		self.content_area = QtWidgets.QScrollArea(
# 			maximumHeight=0, minimumHeight=0
# 		)
# 		self.content_area.setSizePolicy(
# 			QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
# 		)
# 		self.content_area.setFrameShape(QtWidgets.QFrame.NoFrame)

# 		lay = QtWidgets.QVBoxLayout(self)
# 		lay.setSpacing(0)
# 		lay.setContentsMargins(0, 0, 0, 0)
# 		lay.addWidget(self.toggle_button)
# 		lay.addWidget(self.content_area)

# 		self.toggle_animation.addAnimation(
# 			QtCore.QPropertyAnimation(self, b"minimumHeight")
# 		)
# 		self.toggle_animation.addAnimation(
# 			QtCore.QPropertyAnimation(self, b"maximumHeight")
# 		)
# 		self.toggle_animation.addAnimation(
# 			QtCore.QPropertyAnimation(self.content_area, b"maximumHeight")
# 		)

# 	@QtCore.pyqtSlot()
# 	def on_pressed(self):
# 		checked = self.toggle_button.isChecked()
# 		self.toggle_button.setArrowType(
# 			QtCore.Qt.DownArrow if not checked else QtCore.Qt.RightArrow
# 		)
# 		self.toggle_animation.setDirection(
# 			QtCore.QAbstractAnimation.Forward
# 			if not checked
# 			else QtCore.QAbstractAnimation.Backward
# 		)
# 		self.toggle_animation.start()

# 	def setContentLayout(self, layout):
# 		lay = self.content_area.layout()
# 		del lay
# 		self.content_area.setLayout(layout)
# 		collapsed_height = (
# 			self.sizeHint().height() - self.content_area.maximumHeight()
# 		)
# 		content_height = layout.sizeHint().height()
# 		for i in range(self.toggle_animation.animationCount()):
# 			animation = self.toggle_animation.animationAt(i)
# 			animation.setDuration(500)
# 			animation.setStartValue(collapsed_height)
# 			animation.setEndValue(collapsed_height + content_height)

# 		content_animation = self.toggle_animation.animationAt(
# 			self.toggle_animation.animationCount() - 1
# 		)
# 		content_animation.setDuration(500)
# 		content_animation.setStartValue(0)
# 		content_animation.setEndValue(content_height)

class DraggableQLabel(QLabel):
	def __init__(self, text):
		super().__init__(text)

	def mouseMoveEvent(self, evt: QMouseEvent):
		if evt.buttons() == Qt.LeftButton:
			drag = QDrag(self)
			mime: QMimeData = self.GetDragMimeData(evt)
			drag.setMimeData(mime)
			
			pixmap = QPixmap(self.size())
			self.render(pixmap)
			# TODO: find a way to use same mask for pixmap as in self.mask()
			# if hasattr(self, 'maskRegion'):
			# 	pixmap.setMask(self.maskRegion)
			drag.setPixmap(pixmap)
	
			drag.exec_(Qt.MoveAction)
	
	def GetDragMimeData(self, evt: QMouseEvent):
		return QMimeData()

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
		
		# TODO: not a lot of sense without masking ondrag-pixmap in DraggableQLabel
		# path = QPainterPath()
		# path.addRoundedRect(QRectF(self.rect()), rounding, rounding)
		# self.maskRegion = QRegion(path.toFillPolygon().toPolygon())
		# self.setMask(self.maskRegion)
		
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

class QLabelClickable(QLabel):
	clicked = pyqtSignal(QMouseEvent)
	
	# TODO: use @typing.overload for passing text to constructor as well
	def __init__(self, parent: QWidget):
		super(QLabelClickable, self).__init__(parent)
		self.initUI()
	
	def initUI(self):
		self.setCursor(QCursor(Qt.PointingHandCursor))
	
	def mousePressEvent(self, evt: QMouseEvent) -> None:
		self.clicked.emit(evt)
		evt.accept()