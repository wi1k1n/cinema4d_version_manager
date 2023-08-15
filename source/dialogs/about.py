import sys, typing, platform
from functools import partial
from PyQt5 import QtCore, QtGui

from PyQt5.QtCore import Qt, QRectF, QPropertyAnimation, pyqtProperty, QEasingCurve, QObject, QEvent
from PyQt5.QtGui import QIcon, QKeySequence, QFont, QPainterPath, QRegion, QPixmap, QColor, QMouseEvent, QShowEvent, QCursor, QCloseEvent, QFocusEvent
from PyQt5.QtWidgets import (
	QApplication, QLabel, QMainWindow, QMenu, QMenuBar, QToolBar, QAction, QSpinBox, QDialog, QVBoxLayout, QHBoxLayout, QWidget
)

import version
from utils import *
from gui_utils import *

# https://stackoverflow.com/questions/46428856/how-to-make-window-fade-out-slowly-when-i-click-the-close-button-by-pyqt5
# Animation on splash: https://stackoverflow.com/questions/22423781/using-a-gif-in-splash-screen-in-pyqt
class FadeInOutDialog(QDialog):
	def __init__(self, parent: QWidget | None = None):
		super().__init__(parent)

		self.animFadeIn: QPropertyAnimation = QPropertyAnimation(self, b'setWinOpacity')
		self.animFadeIn.setDuration(500)
		self.animFadeIn.setStartValue(0)
		self.animFadeIn.setEndValue(1.)
		self.animFadeIn.setEasingCurve(QEasingCurve(QEasingCurve.InQuad)) # https://doc.qt.io/qt-5/qeasingcurve.html
		
		self.animFadeOut: QPropertyAnimation = QPropertyAnimation(self, b'setWinOpacity')
		self.animFadeOut.setDuration(300)
		self.animFadeOut.setStartValue(1.)
		self.animFadeOut.setEndValue(0)
		self.animFadeOut.setEasingCurve(QEasingCurve(QEasingCurve.OutQuad))
		self.animFadeOut.finished.connect(self._onFadeOutFinished)
		self.fadeOutFinished = False
	
	@pyqtProperty(float)
	def winOpacity(self):
		return self.windowOpacity()
	@winOpacity.setter
	def setWinOpacity(self, val: float):
		self.setWindowOpacity(val)

	def _onFadeOutFinished(self):
		self.fadeOutFinished = True
		self.close()
	
	def showEvent(self, evt: QShowEvent) -> None:
		super().showEvent(evt)
		self.animFadeOut.stop()
		self.animFadeIn.start()
		self.fadeOutFinished = False
	
	def closeEvent(self, evt: QCloseEvent) -> None:
		if self.fadeOutFinished:
			self.fadeOutFinished = False
			super().closeEvent(evt)
			return evt.accept()

		self.animFadeIn.stop()
		self.animFadeOut.start()
		evt.ignore()

class AboutWindow(FadeInOutDialog):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle("About")
		self.setWindowFlags(self.windowFlags() & ~Qt.WindowMinimizeButtonHint | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
		self.setFixedSize(600, 400)
		self.setStyleSheet("background-color: #FFFF33; color: #4D4D4D;")
		
		radius = 12.0
		path = QPainterPath()
		path.addRoundedRect(QRectF(self.rect()), radius, radius)
		self.setMask(QRegion(path.toFillPolygon().toPolygon()))

		regularTextFont: QFont = QLabel().font()
		regularTextFont.setPixelSize(14)

		# First row: Icon + Label
		picLabel: QLabel = QLabel(self)
		pixMap: QPixmap = QPixmap(OsPathJoin(IMAGES_FOLDER, 'icon.png'))
		picLabel.setScaledContents(True)
		picLabel.setPixmap(pixMap)
		picLabel.setFixedSize(54, 54)

		titleLabel: QLabel = QLabel('C4D Version Manager')
		titleFont: QFont = QFont(regularTextFont)
		titleFont.setPixelSize(28)
		titleLabel.setFont(titleFont)
		titleLabelMargins = titleLabel.contentsMargins()
		titleLabelMargins.setLeft(12)
		titleLabel.setContentsMargins(titleLabelMargins)
		
		firstRowLayout: QHBoxLayout = QHBoxLayout()
		firstRowLayout.addWidget(picLabel)
		firstRowLayout.addWidget(titleLabel)
		firstRowLayout.addStretch()

		# Build string
		self.buildStringCopied = False
		self.buildLabel: QLabel = QLabel()
		self.buildLabel.setFont(QFont(regularTextFont))
		buildLabelMargins = self.buildLabel.contentsMargins()
		buildLabelMargins.setTop(40)
		buildLabelMargins.setBottom(20)
		self.buildLabel.setContentsMargins(buildLabelMargins)

		# Other lines
		appNameBoldLabel: QLabel = QLabel('C4D Version & Manager')
		appNameBoldFont: QFont = QFont(regularTextFont)
		appNameBoldFont.setBold(True)
		appNameBoldLabel.setFont(appNameBoldFont)
		copyrightLabel: QLabel = QLabel('© 2023 C4D Manager. All Versions Reserved.')
		copyrightLabel.setFont(QFont(regularTextFont))

		# Contribute line
		contributePicLabel: QLabelClickable = QLabelClickable(self)
		contributePixmap: QPixmap = QPixmap(OsPathJoin(IMAGES_FOLDER, 'github.png'))
		contributePicLabel.setScaledContents(True)
		contributePicLabel.setPixmap(contributePixmap)
		contributePicLabel.setFixedSize(38, 38)
		contributePicLabel.clicked.connect(self.openSourceCodeRepo)

		contributeLabel: QLabelClickable = QLabelClickable(self)
		contributeLabel.setText('Contribute')
		contributeFont: QFont = QFont(regularTextFont)
		contributeFont.setPixelSize(22)
		contributeFont.setStretch(125)
		contributeFont.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.5)
		contributeLabel.setFont(contributeFont)
		contributeLabel.clicked.connect(self.openSourceCodeRepo)
		
		contributeRowLayout: QHBoxLayout = QHBoxLayout()
		contributeRowLayout.addStretch()
		contributeRowLayout.addWidget(contributePicLabel)
		contributeRowLayout.addWidget(contributeLabel)

		# Main layout
		mainLayout: QVBoxLayout = QVBoxLayout()
		mainLayout.setContentsMargins(30, 35, 25, 20)
		mainLayout.addLayout(firstRowLayout)
		mainLayout.addWidget(self.buildLabel)
		mainLayout.addWidget(appNameBoldLabel)
		mainLayout.addWidget(copyrightLabel)
		mainLayout.addStretch()
		mainLayout.addLayout(contributeRowLayout)
		self.setLayout(mainLayout)

		self.isCloseOnLosingFocus = True
	
	def openSourceCodeRepo(self, evt: QMouseEvent):
		OpenURL('https://github.com/wi1k1n/cinema4d_version_manager')
		self.isCloseOnLosingFocus = False
		evt.accept()

	def mousePressEvent(self, evt: QMouseEvent):
		if evt.button() == Qt.RightButton:
			if not self.buildStringCopied:
				copyStr: str = f'{self.buildLabel.text()} {platform.system()} {platform.release()}'
				QApplication.clipboard().setText(copyStr)
				self.buildLabel.setText(self.buildLabel.text() + ' (copied)')
				self.buildStringCopied = True
		else:
			self.close()
		evt.accept()

	def changeEvent(self, evt: QEvent) -> None:
		# print(qEventLookup[str(evt.type())])
		if evt.type() == QEvent.ActivationChange:
			if not self.isActiveWindow() and self.isCloseOnLosingFocus:
				self.close()
				return
			self.isCloseOnLosingFocus = True
		return super().changeEvent(evt)
	
	def showEvent(self, evt: QShowEvent):
		super().showEvent(evt)
		self.buildLabel.setText(f'v{version.C4DL_VERSION} (Build {version.BUILD_VERSION})')
		self.buildStringCopied = False