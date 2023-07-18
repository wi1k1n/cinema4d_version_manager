from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
	QLabel,
	QMainWindow,
	QDialog,
	QHBoxLayout,
	QListWidget,
	QWidget,
	QVBoxLayout,
	QPushButton,
	QListWidgetItem,
	QStackedWidget
)

class PreferencesWindow(QMainWindow):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.categories = {
			'General': self._createPrefGeneral(),
			'Appearance': self._createPrefAppearance(),
			'Search paths': self._createPrefPaths()
		}

		self.setWindowTitle("Preferences")
		self.setWindowFlags(Qt.WindowCloseButtonHint)
		self.resize(400, 200)
		
		# Stack of widgets containing pref entries for each category
		self.contentStack = QStackedWidget()
		for v in self.categories.values():
			if v is not None:
				self.contentStack.addWidget(v)
		self.contentStack.setCurrentIndex(0)
		
		# List with preferences categories
		self.categoriesWidget = QListWidget()
		self.categoriesWidget.setMinimumWidth(150)
		self.categoriesWidget.setMinimumHeight(50)
		for k in self.categories.keys():
			self.categoriesWidget.addItem(k)
		self.categoriesWidget.setFixedWidth(self.categoriesWidget.sizeHintForColumn(0) + 2 * self.categoriesWidget.frameWidth() + 10)
		self.categoriesWidget.currentItemChanged.connect(self._prefCategoryChanged)
		self.categoriesWidget.setCurrentRow(0)
		

		# Main layout of prefs window
		self.prefsLayout: QHBoxLayout = QHBoxLayout()
		self.prefsLayout.addWidget(self.categoriesWidget)
		self.prefsLayout.addWidget(self.contentStack)

		self.centralWidget = QWidget()
		self.centralWidget.setLayout(self.prefsLayout)
		self.setCentralWidget(self.centralWidget)
	
	def _prefCategoryChanged(self, cur: QListWidgetItem, prev):
		if cur is None:
			return
		self.contentStack.setCurrentIndex(self.categoriesWidget.currentRow())

	def _createPrefGeneral(self):
		prefEntriesLayout = QVBoxLayout()
		prefEntriesLayout.addWidget(QLabel("Hello, World"))
		prefEntriesLayout.addWidget(QLabel("Hello, PyQt!"))
		prefEntriesLayout.addWidget(QPushButton("Button"))
		prefEntriesLayout.addStretch()

		prefEntriesWidget = QWidget()
		prefEntriesWidget.setLayout(prefEntriesLayout)

		return prefEntriesWidget

	def _createPrefAppearance(self):
		prefEntriesLayout = QVBoxLayout()
		prefEntriesLayout.addWidget(QLabel("Appearance"))
		prefEntriesLayout.addStretch()

		prefEntriesWidget = QWidget()
		prefEntriesWidget.setLayout(prefEntriesLayout)

		return prefEntriesWidget

	def _createPrefPaths(self):
		prefEntriesLayout = QVBoxLayout()
		prefEntriesLayout.addWidget(QLabel("Path1"))
		prefEntriesLayout.addWidget(QLabel("Path2"))
		prefEntriesLayout.addWidget(QPushButton("Commit"))
		prefEntriesLayout.addStretch()

		prefEntriesWidget = QWidget()
		prefEntriesWidget.setLayout(prefEntriesLayout)

		return prefEntriesWidget
