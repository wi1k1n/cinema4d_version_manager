# https://realpython.com/python-menus-toolbars/#building-context-or-pop-up-menus-in-pyqt
import sys
from PyQt5.QtWidgets import QApplication

import res.qrc_resources
from dialogs.main_window import MainWindow
from dialogs.preferences import PreferencesWindow
from dialogs.about import AboutWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())