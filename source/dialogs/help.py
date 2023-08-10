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


class ShortcutsWindow(QDialog):
	def __init__(self, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		# self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
		
		shortcuts: dict[str, dict[str, str]] = {
			'General': {
				'position': (0, 0),
				'content': {
					# 'Ctrl + O': 			'Add search folder',
					'Ctrl + S': 			'Save c4d cache and tags info',
					'Ctrl + E': 			'Preference',
					'F1': 					'Show this cheatsheet',
					'F5': 					'Update tiles view',
					'Ctrl + F5': 			'Rescan search paths',
					'Ctrl + T': 			'Open/Close Tags window',
					'Ctrl + F': 			'Open/Close Search-Filter-Sort window',
				}
			},
			'Grouping': {
				'position': (1, 0),
				'content': {
					'Ctrl + A': 			'Toggle fold all',
					'Ctrl + G, Ctrl + G': 	'No grouping',
					('Ctrl + 1', 'Ctrl + G, Ctrl + F'): 'Group by search paths',
					('Ctrl + 2', 'Ctrl + G, Ctrl + V'): 'Group by c4d version',
					('Ctrl + 3', 'Ctrl + G, Ctrl + T'): 'Group by tags',
					('Ctrl + 4', 'Ctrl + G, Ctrl + S'): 'Group by c4d status',
					# 'Alt + N': 				'Apply N-th custom grouping view',
					'Empty Double LMB': 	'Apply default grouping view',
				}
			},
			'C4D Tile Widget': {
				'position': (0, 1),
				'content': {
					'LMB': 					'Run C4D',
					'Ctrl + LMB': 			'Run C4D with console',
					'Shift + LMB': 			'Kill C4D process',
					'Ctrl + Shift + LMB': 	'Restart C4D',
					'MMB':		 			'Activate C4D if it\'s running',
					'Ctrl + MMB': 			'Open C4D folder',
					'Shift + MMB': 			'Open C4D preferences folder',
				}
			},
			'Tag management': {
				'position': (1, 1),
				'content': {
					'D&D': 					'Assign tag to C4D',
					'Ctrl + D&D': 			'Insert tag to C4D as first',
					'Shift + D&D': 			'Remove tag assignment from C4D',
					'Ctrl + Double LMB': 	'Edit tag',
					'Double LMB': 			'Group by Tag + isolate current tag',
					'(Empty) Double LMB': 	'Create new tag',
				}
			},
		}
		abbrDecodings: dict[str, str] = {
			'LMB': 'Left Mouse Buttom',
			'MMB': 'Middle Mouse Buttom',
			'RMB': 'Right Mouse Buttom',
			'D&D': 'Drag-n-Drop',
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

		def addExtendedAbbreviationTooltip(lbl: QLabel):
			ret = lbl.text()
			for abbr, val in abbrDecodings.items():
				if abbr not in ret: continue
				ret = ret.replace(abbr, val)
			lbl.setToolTip(ret)
		
		# Create corresponding widgets
		def createCaptionLabel(txt: str) -> QLabel:
			lbl: QLabel = QLabel(txt)
			font: QFont = QFont(APPLICATION_FONT_FAMILY, 11)
			font.setBold(True)
			lbl.setFont(font)
			lbl.setContentsMargins(QMargins(10, 10, 0, 0))
			return lbl
		def createShortcutLabel(txt: tuple[str] | str) -> QLabel:
			text: str = txt
			if isinstance(txt, tuple):
				if len(txt) == 1:
					text = txt[0]
				else:
					POSTFIX = ' or\n'
					text = ''
					for sc in txt:
						text += sc + POSTFIX
					text = text[:len(text) - len(POSTFIX)]
			lbl: QLabel = QLabel(text)
			lbl.setFont(QFont(APPLICATION_FONT_FAMILY, 10))
			lbl.setMaximumWidth(128)
			addExtendedAbbreviationTooltip(lbl)
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
		self.setFixedSize(800, 500)

class TrackBugsWindow(QDialog):
	def __init__(self, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self.setWindowTitle('C4D Version Manager: Report a bug')

		infoLabel: QLabel = QLabel('External bug tracking is usually better:', self)
		infoLabel.setAlignment(Qt.AlignCenter)
		infoLabel.setFont(QFont(APPLICATION_FONT_FAMILY, 14))

		linkLabel: QLabel = QLabel('<a href="https://github.com/wi1k1n/cinema4d_version_manager/issues">https://github.com/wi1k1n/cinema4d_version_manager/issues</a>', self)
		linkLabel.setFont(QFont(APPLICATION_FONT_FAMILY, 12))
		linkLabel.setOpenExternalLinks(True)
		linkLabel.setTextInteractionFlags(Qt.TextBrowserInteraction)
		linkLabel.setTextFormat(Qt.RichText)

		layout: QVBoxLayout = QVBoxLayout()
		layout.addWidget(infoLabel)
		layout.addWidget(linkLabel)

		self.setLayout(layout)
		minSize: QSize = self.minimumSizeHint()
		self.setFixedSize(minSize.width() + 20, minSize.height() + 20)