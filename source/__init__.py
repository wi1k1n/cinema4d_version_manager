import sys, random, os
from functools import partial
from typing import List

# Tweak Windows app group for the custom icon to be used instead of Python one
try:
    from ctypes import windll  # Only exists on Windows.
    myappid = 'wi1k1n.c4dtools.c4dvmanager.001'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QSplashScreen

import res.qrc_resources
import version
from dialogs.main_window import MainWindow, TestMainWindow
from dialogs.preferences import PreferencesWindow
from dialogs.about import AboutWindow
from gui_utils import *
from utils import *
	
# TODO: here for now, please remove once not needed!
def testApp():
	app: QApplication = QApplication(sys.argv)
	win: TestMainWindow = TestMainWindow()
	win.show()
	sys.exit(app.exec_())

# Extensive PyQt tutorial: https://realpython.com/python-menus-toolbars/#building-context-or-pop-up-menus-in-pyqt
class C4DVersionManagerApplication(QApplication):
	def __init__(self, argv: List[str]) -> None:
		super().__init__(argv)
		
		self.mainWindow: MainWindow = MainWindow()
		self.mainWindow.hideToTraySignal.connect(self._hideToTray)

		self.iconApp: QIcon = QIcon(os.path.join(IMAGES_FOLDER, 'icon.png'))
		self.setWindowIcon(self.iconApp)
		
		font: QFont = self.font()
		# font.setPixelSize(16)
		self.setFont(font)

		self.initTray()

		self.mainWindow.show()
		self.mainWindow.FirstRunHandler()
	
	def initTray(self):
		actionExit: QAction = QAction('Exit')
		actionExit.triggered.connect(sys.exit)
		trayMenu: QMenu = QMenu()
		trayMenu.addAction(actionExit)

		self.trayIcon: QSystemTrayIcon = QSystemTrayIcon()
		self.trayIcon.setIcon(self.iconApp)
		self.trayIcon.setContextMenu(trayMenu)
		self.trayIcon.activated.connect(self._activateFromTray)
		self.trayIcon.setVisible(False)
	
	def _activateFromTray(self, reason):
		if reason != QSystemTrayIcon.ActivationReason.Context and self.mainWindow.isHidden():
			self.mainWindow.show()
			self.mainWindow.activateWindow()
			self.trayIcon.setVisible(False)
			# win.restoreState()

	def _hideToTray(self):
		self.trayIcon.setVisible(True)

if __name__ == "__main__":
	version._loadBuildInfo(os.getcwd())
	app: C4DVersionManagerApplication = C4DVersionManagerApplication(sys.argv)
	sys.exit(app.exec_())
	
	# testApp()
	# # https://stackoverflow.com/a/52617714
	# w = QtWidgets.QMainWindow()
	# w.setCentralWidget(QtWidgets.QWidget())
	# dock = QtWidgets.QDockWidget("Collapsible Demo")
	# w.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock)
	# scroll = QtWidgets.QScrollArea()
	# dock.setWidget(scroll)
	# content = QtWidgets.QWidget()
	# scroll.setWidget(content)
	# scroll.setWidgetResizable(True)
	# vlay = QtWidgets.QVBoxLayout(content)
	# for i in range(10):
	# 	box = CollapsibleBox("Collapsible Box Header-{}".format(i))
	# 	vlay.addWidget(box)
	# 	lay = QtWidgets.QVBoxLayout()
	# 	for j in range(8):
	# 		label = QtWidgets.QLabel("{}".format(j))
	# 		color = QtGui.QColor(*[random.randint(0, 255) for _ in range(3)])
	# 		label.setStyleSheet(
	# 			"background-color: {}; color : white;".format(color.name())
	# 		)
	# 		label.setAlignment(QtCore.Qt.AlignCenter)
	# 		lay.addWidget(label)

	# 	box.setContentLayout(lay)
	# vlay.addStretch()
	# w.resize(640, 480)
	# w.show()