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
	QLayoutItem,
	QScrollArea,
	QComboBox,
	QGroupBox,
	QCheckBox,
)

from version import *
from gui_utils import *
from utils import *

# Might be helpful for searchbox: https://stackoverflow.com/questions/44264852/pyside-pyqt-overlay-widget
class FilterSortWindow(QDockWidget):
	def __init__(self, parent=None):
		super().__init__(parent)

		self.setWindowTitle("Filter/Sort")
		self.setWindowFlags(self.windowFlags() & Qt.WindowCloseButtonHint)
		self.resize(400, 400)
		self.setMinimumWidth(150)

		mainLayout: QVBoxLayout = QVBoxLayout()

		# TODO: Temporarily blocked to get some checkpoint in development
		self.setDisabled(True)
		self.disabledDisclaimer = QLabel(f'!!! WARNING !!!{os.linesep}Search / Filter / Sort functionality is not available in this release')
		self.disabledDisclaimer.setStyleSheet('color: rgb(160, 0, 0)')
		disclFont = self.disabledDisclaimer.font()
		disclFont.setPixelSize(12)
		self.disabledDisclaimer.setFont(disclFont)
		mainLayout.addWidget(self.disabledDisclaimer)

		presetsWidget: QWidget = self._createPresetsWidget()
		searchWidget: QWidget = self._createSearchWidget()
		filterWidget: QWidget = self._createFilterWidget()
		sortWidget: QWidget = self._createSortWidget()

		mainLayout.addWidget(presetsWidget)
		mainLayout.addWidget(searchWidget)
		mainLayout.addWidget(filterWidget)
		mainLayout.addWidget(sortWidget)
		mainLayout.addStretch()
		
		mainArea: QWidget = QWidget(self)
		mainArea.setLayout(mainLayout)
		self.setWidget(mainArea)

		# widget = QWidget(mainArea)
		# # widget.setMinimumWidth(self.minimumWidth())

		# self.flowLayout = FlowLayout(widget)
		# # self.LoadTags()
		# for i in range(5):
		# 	self._addTag(f'string#{i}')

		# mainArea.setWidget(widget)
		# self.setWidget(mainArea)

		# self.setContextMenuPolicy(Qt.ActionsContextMenu)
	
	def _createPresetsWidget(self) -> QWidget:
		presetsWidget: QWidget = QWidget(self)
		presetsLayout: QHBoxLayout = QHBoxLayout()
		presetsWidget.setLayout(presetsLayout)

		label: QLabel = QLabel('Preset:')
		comboPreset: QComboBox = QComboBox(self)
		savePreset: QPushButton = QPushButton('Save', self)
		removePreset: QPushButton = QPushButton('Remove', self)

		presetsLayout.addWidget(label)
		presetsLayout.addWidget(comboPreset)
		presetsLayout.addWidget(savePreset)
		presetsLayout.addWidget(removePreset)

		label.setFixedWidth(label.minimumSizeHint().width())
		savePreset.setFixedWidth(savePreset.minimumSizeHint().width())
		removePreset.setFixedWidth(removePreset.minimumSizeHint().width())

		return presetsWidget

	def _createSearchWidget(self) -> QWidget:
		mainWidget: QGroupBox = QGroupBox(self)
		mainWidget.setTitle('Search')
		mainLayout: QVBoxLayout = QVBoxLayout()
		mainWidget.setLayout(mainLayout)

		# First row
		editSearchBox: QLineEdit = QLineEdit(self)
		searchButton: QPushButton = QPushButton('🔍', self)
		searchButton.setFixedWidth(searchButton.minimumSizeHint().width())
		
		searchBoxLayout: QHBoxLayout() = QHBoxLayout()
		searchBoxLayout.addWidget(editSearchBox)
		searchBoxLayout.addWidget(searchButton)
		
		# Second row
		searchableContentButtons: list[QPushButton] = list()
		for t in ('All', 'Notes', 'Paths'):
			btn: QPushButton = QPushButton(t, self)
			btn.setCheckable(True)
			searchableContentButtons.append(btn)
		
		searchCaseSensitiveButton: QPushButton = QPushButton('CS')
		searchCaseSensitiveButton.setToolTip('Case Sensitive')
		searchCaseSensitiveButton.setCheckable(True)
		searchRegexButton: QPushButton = QPushButton('Regex')
		searchRegexButton.setCheckable(True)
		
		searchSettingsLayout: QHBoxLayout() = QHBoxLayout()
		for btn in searchableContentButtons:
			searchSettingsLayout.addWidget(btn)
		searchSettingsLayout.addStretch()
		searchSettingsLayout.addWidget(searchCaseSensitiveButton)
		searchSettingsLayout.addWidget(searchRegexButton)

		# Third row

		mainLayout.addLayout(searchBoxLayout)
		mainLayout.addLayout(searchSettingsLayout)
		
		return mainWidget

	def _createFilterWidget(self) -> QWidget:
		mainWidget: QGroupBox = QGroupBox(self)
		mainWidget.setTitle('Filter')
		mainLayout: QVBoxLayout = QVBoxLayout()
		mainWidget.setLayout(mainLayout)

		# Tags
		cbTags: QCheckBox = QCheckBox(self)
		lblTags: QLabel = QLabel('Tags:')
		tagsWidget: QWidget = QWidget(self)
		
		tagsRowLayout: QHBoxLayout = QHBoxLayout()
		tagsRowLayout.addWidget(cbTags)
		tagsRowLayout.addWidget(lblTags)
		tagsRowLayout.addWidget(tagsWidget)
		tagsRowLayout.addStretch()

		tagsWidget.setMinimumWidth(self.minimumSizeHint().width())
		tagsFlowLayout: FlowLayout = FlowLayout(tagsWidget)
		tagsWidget.setLayout(tagsFlowLayout)
		
		for t in ('beta', 'alpha', 'exchange', 'main', 'customer', 'package', 'stale'):
			bubble: BubbleWidget = BubbleWidget(t)
			tagsFlowLayout.addWidget(bubble)
		
		mainLayout.addLayout(tagsRowLayout)

		return mainWidget

	def _createSortWidget(self) -> QWidget:
		mainWidget: QGroupBox = QGroupBox(self)
		mainWidget.setTitle('Sort')
		mainLayout: QVBoxLayout = QVBoxLayout()
		mainWidget.setLayout(mainLayout)

		return mainWidget
