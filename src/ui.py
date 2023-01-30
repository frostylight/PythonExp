from pathlib import Path

from PySide6.QtCore import Qt, SignalInstance
from PySide6.QtGui import QAction, QCloseEvent, QKeySequence
from PySide6.QtWidgets import QFileDialog, QGridLayout, QMainWindow, QMenu, QSplitter, QWidget

from src.Lwidget import Console, Explorer, TabManager, EditorTab
from src.Lcore import PythonSyntax


class EditorTabManager(TabManager):
	def __init__(self, parent: QWidget | None) -> None:
		super().__init__(parent)

	def addTab(self, tab: EditorTab, text: str = None) -> int:
		if text is None:
			text = tab.title
		PythonSyntax(tab.document())
		return super().addTab(tab, text)

	def widget(self, index: int) -> EditorTab | None:
		ret = super().widget(index)
		if isinstance(ret, EditorTab):  # always True
			return ret
		else:
			return None

	def currentWidget(self) -> EditorTab | None:
		ret = super().currentWidget()
		if isinstance(ret, EditorTab):  # always True
			return ret
		else:
			return None


class Ui_Main(QMainWindow):
	def __init__(self, parent: QWidget = None) -> None:
		super().__init__(parent)
		self.setWindowTitle("Code")
		self.resize(1080, 720)
		self.__build_main()
		self.__build_menu()
		self.__build_connect()

	def __build_main(self) -> None:
		centralWidget = QWidget(self)
		layout = QGridLayout(centralWidget)
		centralWidget.setLayout(layout)

		self._splitter_horizon = QSplitter(Qt.Orientation.Horizontal, centralWidget)
		self._splitter_vertical = QSplitter(Qt.Orientation.Vertical, self._splitter_horizon)
		self.explorer = Explorer(self._splitter_horizon)
		self.tabManager = EditorTabManager(self._splitter_vertical)
		self.console = Console(self._splitter_vertical)

		self._splitter_horizon.addWidget(self.explorer)
		self._splitter_horizon.addWidget(self._splitter_vertical)
		self._splitter_vertical.addWidget(self.tabManager)
		self._splitter_vertical.addWidget(self.console)
		self.explorer.setMinimumSize(200, 0)
		self.console.setMinimumSize(0, 150)
		self._splitter_vertical.setSizes([720, 150])
		self._splitter_horizon.setSizes([200, 1080])
		sizePolicy = self._splitter_vertical.sizePolicy()
		sizePolicy.setHorizontalStretch(1)
		self._splitter_vertical.setSizePolicy(sizePolicy)
		layout.addWidget(self._splitter_horizon)
		self.setCentralWidget(centralWidget)

	def __build_menu(self) -> None:
		Key = QKeySequence.StandardKey
		self._action_openFile = QAction(text="打开文件", triggered=self.openFile, shortcut=Key.Open)
		self._action_openDir = QAction(text="打开文件夹", triggered=self.openDir, shortcut="Ctrl+Alt+K")
		self._action_saveFile = QAction(text="保存", triggered=self.saveFile, shortcut=Key.Save)
		self._action_saveAs = QAction(text="另存为...", triggered=self.saveFileAs, shortcut=Key.SaveAs)
		self._action_copy = QAction(text="复制", triggered=self.copyText, shortcut=Key.Copy)
		self._action_cut = QAction(text="剪切", triggered=self.cutText, shortcut=Key.Cut)
		self._action_paste = QAction(text="粘贴", triggered=self.pasteText, shortcut=Key.Paste)
		self._action_run = QAction(text="运行", triggered=self.runCode, shortcut="Shift+F")
		self._action_stop = QAction(text="停止", triggered=self.console.stop, shortcut="Alt+Shift+F")

		menuBar = self.menuBar()

		self._menu_file = QMenu("文件", menuBar)

		self._menu_file.addAction(self._action_openFile)
		self._menu_file.addAction(self._action_openDir)
		self._menu_file.addSeparator()
		self._menu_file.addAction(self._action_saveFile)
		self._menu_file.addAction(self._action_saveAs)
		menuBar.addAction(self._menu_file.menuAction())

		self._menu_edit = QMenu("编辑", menuBar)
		self._menu_edit.addAction(self._action_copy)
		self._menu_edit.addAction(self._action_cut)
		self._menu_edit.addAction(self._action_paste)
		menuBar.addAction(self._menu_edit.menuAction())

		self._menu_run = QMenu("运行", menuBar)
		self._menu_run.addAction(self._action_run)
		self._menu_run.addAction(self._action_stop)
		menuBar.addAction(self._menu_run.menuAction())

		self.__consoleStateChanged(False)
		self.__tabCountChanged(0)

	def __build_connect(self) -> None:
		self.explorer.selectFile.connect(self.__addTab)
		self.console.stateChanged.connect(self.__consoleStateChanged)
		self.tabManager.countChanged.connect(self.__tabCountChanged)

	def __addTab(self, path: Path | None) -> None:
		for i in range(self.tabManager.count()):
			if self.tabManager.widget(i).path.samefile(path):
				self.tabManager.setCurrentIndex(i)
				return
		tab = EditorTab(self.tabManager, path)
		self.tabManager.setCurrentIndex(self.tabManager.addTab(tab))

	def __consoleStateChanged(self, state: bool) -> None:
		self._action_run.setEnabled(not state)
		self._action_stop.setEnabled(state)

	def __tabCountChanged(self, count: int) -> None:
		self._action_saveFile.setEnabled(count > 0)
		self._action_saveAs.setEnabled(count > 0)
		self._menu_edit.setEnabled(count > 0)

	def openFile(self) -> None:
		filename, _ = QFileDialog.getOpenFileName(self, caption="打开文件", filter='*.py')
		if not filename:
			return
		self.__addTab(Path(filename))

	def openDir(self) -> None:
		path = QFileDialog.getExistingDirectory(caption="打开文件夹")
		if not path:
			return
		self.explorer.setPath(Path(path))

	def saveFile(self) -> None:
		self.tabManager.currentWidget().save()

	def saveFileAs(self) -> None:
		self.tabManager.currentWidget().saveAs()

	def copyText(self) -> None:
		self.tabManager.currentWidget().copy()

	def cutText(self) -> None:
		self.tabManager.currentWidget().cut()

	def pasteText(self) -> None:
		self.tabManager.currentWidget().paste()

	def runCode(self) -> None:
		tab = self.tabManager.currentWidget()
		if tab is not None:
			self.console.execute(tab.path)

	def closeEvent(self, event: QCloseEvent) -> None:
		self.console.stop()
		if not self.tabManager.close():
			event.ignore()
			return
		super().closeEvent(event)
