import sys, os, typing, datetime as dt, json
from subprocess import Popen, PIPE
from functools import partial

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import (
    QObject, Qt, QEvent, pyqtSignal, QProcess, QRect, QPoint, QPropertyAnimation, QMargins
)
from PyQt5.QtGui import (
    QIcon, QKeySequence, QPixmap, QFont, QCursor, QMouseEvent, QDropEvent, QDragEnterEvent,
    QKeyEvent, QCloseEvent, QPaintEvent, QPainter, QColor, QBrush, QPen
)
from PyQt5.QtWidgets import (
	QApplication, QLabel, QMainWindow, QMenu, QMenuBar, QStyle, QStyleHintReturn, QStyleOption,
	QToolBar, QAction, QWidget, QTabWidget, QLayout, QVBoxLayout, QHBoxLayout, QFrame,
	QScrollArea, QGroupBox, QTreeWidget, QTreeWidgetItem, QStatusBar, QProxyStyle, QInputDialog,
	QPlainTextEdit, QShortcut, QGridLayout
)

# import qrc_resources
from dialogs.preferences import PreferencesWindow
from dialogs.about import AboutWindow
from dialogs.tags import TagsWindow, C4DTag, TagBubbleWidget
from version import *
from utils import *
from gui_utils import *


class ShortcutsWindow(QWidget):
	def __init__(self, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		
		shortcuts: dict[str, dict[str, str]] = {
			'General': {
				'position': (0, 0),
				'content': {
					'Ctrl + S': 			'Save c4d cache and tags info',
					'Ctrl + E': 			'Preference',
					'F1': 					'Show this cheatsheet',
					'Ctrl + F5': 			'Rescan',
					'Ctrl + T': 			'Open Tags window',
					'Ctrl + F': 			'Open Search/Filter/Sort window',
				}
			},
			'Grouping': {
				'position': (1, 0),
				'content': {
					'Ctrl + G, Ctrl + G': 	'Toggle fold all',
					'Ctrl + G, Ctrl + N': 	'No grouping',
					'Ctrl + G, Ctrl + F': 	'Group by search paths',
					'Ctrl + G, Ctrl + V': 	'Group by c4d version',
					'Ctrl + G, Ctrl + T': 	'Group by tags',
					'Ctrl + G, Ctrl + S': 	'Group by c4d status',
				}
			},
			'C4D Tile Mouse': {
				'position': (0, 1),
				'content': {
					'LMB': 					'Run C4D',
					'Ctrl + LMB': 			'Run C4D with console',
					'Shift + LMB': 			'Open C4D folder',
					'Ctrl + Shift + LMB': 	'Rescan',
					'MMB':		 			'Activate C4D if it\'s running',
					'Shift + MMB': 			'Kill C4D process',
					'Ctrl + Shift + MMB': 	'Restart C4D',
				}
			},
			'Tag management': {
				'position': (1, 1),
				'content': {
					'Tag D&D': 				'Assign tag to C4D',
					'Tag Ctrl + D&D': 		'Insert tag to C4D as first',
					'Tag Shift + D&D': 		'Remove tag assignment from C4D',
					'Tag Ctrl + Double LMB': 'Group by Tag + isolate current tag',
					'Tag Double LMB': 		'Edit tag',
					'Empty Double LMB': 	'Create new tag',
				}
			},
		}

		self.setWindowTitle('Shortcuts Cheatsheet')

		grid: QGridLayout = QGridLayout()
		grid.setHorizontalSpacing(20)
		self.setLayout(grid)
		
		# First pre-calculate actual grid positions
		posToCatMap: dict[tuple[int, int], str] = {o['position']: k for k, o in shortcuts.items()}
		catPositions = [o['position'] for o in shortcuts.values()]
		catRowIndices, catColIndices = zip(*catPositions)
		catRowIdxSet, catColIdxSet = set(catRowIndices), set(catColIndices)
		for curColIdx in catColIdxSet:
			keysAndRowIndices = list({(posToCatMap[(rowIdx, curColIdx)], rowIdx) for rowIdx in catRowIdxSet if (rowIdx, curColIdx) in posToCatMap})
			keysAndRowIndices.sort(key=lambda x: x[1])
			rowCursor = 0
			for (k, rowIdx) in keysAndRowIndices:
				shortcuts[k]['_gridRowOffset'] = rowCursor
				rowCursor += len(shortcuts[k]['content']) + 1

		# Create corresponding widgets
		def createCaptionLabel(txt: str) -> QLabel:
			lbl: QLabel = QLabel(txt)
			font: QFont = QFont(APPLICATION_FONT_FAMILY, 11)
			font.setBold(True)
			lbl.setFont(font)
			lbl.setContentsMargins(QMargins(10, 10, 0, 0))
			return lbl
		def createShortcutLabel(txt: str) -> QLabel:
			lbl: QLabel = QLabel(txt)
			lbl.setFont(QFont(APPLICATION_FONT_FAMILY, 10))
			lbl.setMaximumWidth(128)
			return lbl
		def createDescriptionLabel(txt: str) -> QLabel:
			lbl: QLabel = QLabel(txt)
			lbl.setFont(QFont(APPLICATION_FONT_FAMILY, 9))
			lbl.setWordWrap(True)
			return lbl
		
		for sectionName, obj in shortcuts.items():
			pr = obj['_gridRowOffset']
			pc = obj['position'][1] * 2
			grid.addWidget(createCaptionLabel(sectionName), pr, pc, 1, 2, Qt.AlignCenter)
			for idx, (shortcut, description) in enumerate(obj['content'].items()):
				cr, cc = pr + idx + 1, pc
				grid.addWidget(createShortcutLabel(shortcut), cr, cc, 1, 1)
				grid.addWidget(createDescriptionLabel(description), cr, cc + 1, 1, 1)
		
		# self.setFixedSize(self.size())
		self.setFixedWidth(800)