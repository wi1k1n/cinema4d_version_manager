import sys, random, os
from functools import partial

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

# Extensive tutorial: https://realpython.com/python-menus-toolbars/#building-context-or-pop-up-menus-in-pyqt
# Animation on splash: https://stackoverflow.com/questions/22423781/using-a-gif-in-splash-screen-in-pyqt
if __name__ == "__main__":
	# testApp()
	version._loadBuildInfo(os.getcwd())
	app: QApplication = QApplication(sys.argv)

	icon: QIcon = QIcon(os.path.join(IMAGES_FOLDER, 'icon.png'))
	app.setWindowIcon(icon)
	font: QFont = app.font()
	# font.setPixelSize(16)
	app.setFont(font)

	win: MainWindow = MainWindow()
	win.show()
	win.FirstRunHandler()

	actionExit: QAction = QAction('Exit')
	actionExit.triggered.connect(sys.exit)
	trayMenu: QMenu = QMenu()
	trayMenu.addAction(actionExit)

	tray: QSystemTrayIcon = QSystemTrayIcon()
	tray.setIcon(icon)
	tray.setVisible(True)
	tray.setContextMenu(trayMenu)

	def trayActivated(reason):
		if reason != QSystemTrayIcon.ActivationReason.Context and win.isHidden():
			win.show()
			win.activateWindow()
			# win.restoreState()
	tray.activated.connect(trayActivated)
	
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
	
	sys.exit(app.exec_())