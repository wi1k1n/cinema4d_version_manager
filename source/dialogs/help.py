import sys, os, typing, datetime as dt, json
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
	QShortcut
)

# import qrc_resources
from dialogs.preferences import PreferencesWindow
from dialogs.about import AboutWindow
from dialogs.tags import TagsWindow, C4DTag, TagBubbleWidget
from version import *
from utils import *
from gui_utils import *


class HelpWindow(QWidget):
	def __init__(self, parent: QWidget | None = None) -> None:
		super().__init__(parent)