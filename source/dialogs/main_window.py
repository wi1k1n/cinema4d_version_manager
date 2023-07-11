import sys
from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (
    QApplication, QLabel, QMainWindow, QMenu, QMenuBar, QToolBar, QAction, QSpinBox
)

# import qrc_resources
from dialogs.preferences import PreferencesWindow

class MainWindow(QMainWindow):
    """Main Window."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("C4D Selector")
        self.resize(800, 600)

        self.dialogs = {
            'preferences': PreferencesWindow()
        }

        self.centralWidget = QLabel("Hello, World")
        self.centralWidget.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.setCentralWidget(self.centralWidget)

        self._createActions()
        self._createMenuBar()
        self._createToolBars()
        self._createContextMenu()
        self._createStatusBar()
        self._connectActions()
        
    def _createMenuBar(self):
        menuBar = self.menuBar()
        
        fileMenu = menuBar.addMenu('&File')
        # fileMenu.addAction(self.newAction)
        # fileMenu.addAction(self.openAction)
        # self.openRecentMenu = fileMenu.addMenu("Open Recent")
        # fileMenu.addAction(self.saveAction)
        # fileMenu.addSeparator()
        fileMenu.addAction(self.prefsAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAction)
        
        # editMenu = menuBar.addMenu("&Edit")
        # editMenu.addAction(self.copyAction)
        # editMenu.addAction(self.pasteAction)
        # editMenu.addAction(self.cutAction)
        # editMenu.addSeparator()
        # # Find and Replace submenu in the Edit menu
        # findMenu = editMenu.addMenu("Find and Replace")
        # findMenu.addAction("Find...")
        # findMenu.addAction("Replace...")
        
        helpMenu = menuBar.addMenu("&Help")
        # helpMenu.addAction(self.helpContentAction)
        helpMenu.addAction(self.aboutAction)
        
    def _createToolBars(self):
        # fileToolBar = self.addToolBar("File")
        # fileToolBar.addAction(self.newAction)
        # fileToolBar.addAction(self.openAction)
        # fileToolBar.addAction(self.saveAction)

        # editToolBar = self.addToolBar("Edit")
        # editToolBar.addAction(self.copyAction)
        # editToolBar.addAction(self.pasteAction)
        # editToolBar.addAction(self.cutAction)
        # editToolBar.addSeparator()
        # # Spinbox
        # self.fontSizeSpinBox = QSpinBox()
        # self.fontSizeSpinBox.setFocusPolicy(Qt.NoFocus)
        # editToolBar.addWidget(self.fontSizeSpinBox)
        pass
        
    def _createActions(self):
        # # Creating action using the first constructor
        # self.newAction = QAction(QIcon(":file-svgrepo-com.svg"), "&New", self)
        # self.openAction = QAction(QIcon(":camera-svgrepo-com.svg"), "&Open...", self)
        # self.saveAction = QAction(QIcon(":cursor-click-svgrepo-com.svg"), "&Save", self)
        self.prefsAction = QAction(QIcon(":preferences.svg"), "&Preferences", self)
        self.exitAction = QAction("&Exit", self)
        # self.copyAction = QAction("&Copy", self)
        # self.pasteAction = QAction("&Paste", self)
        # self.cutAction = QAction("C&ut", self)
        # self.helpContentAction = QAction("&Help Content", self)
        self.aboutAction = QAction("&About", self)
        
        # # Using string-based key sequences
        # self.newAction.setShortcut("Ctrl+N")
        # self.openAction.setShortcut("Ctrl+O")
        # self.saveAction.setShortcut("Ctrl+S")
        self.prefsAction.setShortcut("Ctrl+E")
        
        # self.copyAction.setShortcut(QKeySequence.Copy)
        # self.pasteAction.setShortcut(QKeySequence.Paste)
        # self.cutAction.setShortcut(QKeySequence.Cut)
        
        # # Adding help tips
        # newTip = "Create a new file"
        # self.newAction.setStatusTip(newTip)
        # self.newAction.setToolTip(newTip)
    
    def _createContextMenu(self):
        # Setting contextMenuPolicy
        self.centralWidget.setContextMenuPolicy(Qt.ActionsContextMenu)
        # # Populating the widget with actions
        # self.centralWidget.addAction(self.newAction)
        # self.centralWidget.addAction(self.openAction)
        # self.centralWidget.addAction(self.saveAction)
        # separator = QAction(self)
        # separator.setSeparator(True)
        # self.centralWidget.addAction(separator)
        # self.centralWidget.addAction(self.copyAction)
        # self.centralWidget.addAction(self.pasteAction)
        # self.centralWidget.addAction(self.cutAction)
        
    def _createStatusBar(self):
        self.statusbar = self.statusBar()
        # # Adding a temporary message
        # self.statusbar.showMessage("Ready", 3000)
        # # Adding a permanent message
        # self.wcLabel = QLabel(f"{self.getWordCount()} Words")
        # self.statusbar.addPermanentWidget(self.wcLabel)
        
    def _connectActions(self):
        # # Connect File actions
        # self.newAction.triggered.connect(self.newFile)
        # self.openAction.triggered.connect(self.openFile)
        # self.openRecentMenu.aboutToShow.connect(self.populateOpenRecent)
        # self.saveAction.triggered.connect(self.saveFile)
        self.prefsAction.triggered.connect(self.openPreferences)
        self.exitAction.triggered.connect(self.close)
        # # Connect Edit actions
        # self.copyAction.triggered.connect(self.copyContent)
        # self.pasteAction.triggered.connect(self.pasteContent)
        # self.cutAction.triggered.connect(self.cutContent)
        # # Connect Help actions
        # self.helpContentAction.triggered.connect(self.helpContent)
        self.aboutAction.triggered.connect(self.about)

    # def newFile(self):
    #     self.centralWidget.setText("<b>File > New</b> clicked")
    # def openFile(self):
    #     self.centralWidget.setText("<b>File > Open...</b> clicked")
    # def openRecentFile(self, filename):
    #     self.centralWidget.setText(f"<b>{filename}</b> opened")
    # def saveFile(self):
    #     self.centralWidget.setText("<b>File > Save</b> clicked")
    def openPreferences(self):
        if ('preferences' in self.dialogs):
            self.dialogs['preferences'].show()
    # def copyContent(self):
    #     self.centralWidget.setText("<b>Edit > Copy</b> clicked")
    # def pasteContent(self):
    #     self.centralWidget.setText("<b>Edit > Paste</b> clicked")
    # def cutContent(self):
    #     self.centralWidget.setText("<b>Edit > Cut</b> clicked")
    # def helpContent(self):
    #     self.centralWidget.setText("<b>Help > Help Content...</b> clicked")
    def about(self):
        self.centralWidget.setText("<b>Help > About...</b> clicked")
    
    # def populateOpenRecent(self):
    #     # Step 1. Remove the old options from the menu
    #     self.openRecentMenu.clear()
    #     # Step 2. Dynamically create the actions
    #     actions = []
    #     filenames = [f"File-{n}" for n in range(5)]
    #     for filename in filenames:
    #         action = QAction(filename, self)
    #         action.triggered.connect(partial(self.openRecentFile, filename))
    #         actions.append(action)
    #     # Step 3. Add the actions to the menu
    #     self.openRecentMenu.addActions(actions)
    
    # def getWordCount(self):
    #     # Logic for computing the word count goes here...
    #     return 42