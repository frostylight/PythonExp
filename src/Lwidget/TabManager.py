from PySide6.QtWidgets import QTabWidget, QWidget, QTabBar
from PySide6.QtCore import QEvent, SignalInstance


class TabBar(QTabBar):
	def __init__(self, parent: QWidget = None) -> None:
		super().__init__(parent)
		self.setTabsClosable(True)
		self.setMovable(True)


class TabManager(QTabWidget):
	tabCloseRequested: SignalInstance

	def __init__(self, parent: QWidget = None) -> None:
		super().__init__(parent)
		self.setTabBar(TabBar(self))
		self.tabCloseRequested.connect(self.__closeTab)

	def __closeTab(self, index: int) -> None:
		self.widget(index).close()
		self.removeTab(index)
