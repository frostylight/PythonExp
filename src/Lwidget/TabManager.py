from PySide6.QtCore import SignalInstance
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QTabBar, QTabWidget, QWidget


class TabBar(QTabBar):
	def __init__(self, parent: QWidget = None) -> None:
		super().__init__(parent)
		self.setTabsClosable(True)
		self.setMovable(True)


class TabManager(QTabWidget):
	tabCloseRequested: SignalInstance
	currentChanged: SignalInstance

	def __init__(self, parent: QWidget = None) -> None:
		super().__init__(parent)
		self.setTabBar(TabBar(self))
		self.tabCloseRequested.connect(self.__closeTab)

	def setTabTextByWidget(self, widget: QWidget, text: str) -> None:
		index = self.indexOf(widget)
		if index < 0 or index >= self.count():
			return
		self.setTabText(index, text)

	def __closeTab(self, index: int) -> None:
		if self.widget(index).close():
			self.removeTab(index)

	def closeEvent(self, event: QCloseEvent) -> None:
		for index in reversed(range(self.count())):
			self.setCurrentIndex(index)
			if not self.widget(index).close():
				event.ignore()
				return
			self.removeTab(index)
		super().closeEvent(event)
