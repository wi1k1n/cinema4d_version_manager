import random
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication

import res.qrc_resources
from dialogs.main_window import MainWindow
from dialogs.preferences import PreferencesWindow
from dialogs.about import AboutWindow
from gui_utils import *

# https://realpython.com/python-menus-toolbars/#building-context-or-pop-up-menus-in-pyqt
if __name__ == "__main__":
	app = QApplication(sys.argv)

	win = MainWindow()
	win.show()
	
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