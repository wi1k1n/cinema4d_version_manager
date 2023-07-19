import sys
from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (
    QApplication, QLabel, QMainWindow, QMenu, QMenuBar, QToolBar, QAction, QSpinBox
)

import version

class AboutWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMinimizeButtonHint)
        self.setFixedSize(240, 80)

        self.centralWidget = QLabel("Cinema 4D instances lister"
                                    + f"\n\nVersion: {version.C4DL_VERSION}")
        self.centralWidget.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.setCentralWidget(self.centralWidget)
