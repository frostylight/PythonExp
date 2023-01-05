from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QCloseEvent, QKeySequence
from PySide6.QtWidgets import QFileDialog, QGridLayout, QMainWindow, QMenu, QSplitter, QWidget

from Lwidget import Console, DirView, Editor
from Lcore import PythonSyntax


class Ui_Main(QMainWindow):
	def __init__(self) -> None:
		super().__init__()
		self.setup()

	def closeEvent(self, ev: QCloseEvent) -> None:
		self.console.stop()
		self.editor.checkSave()
		super().closeEvent(ev)

	def console_run(self) -> None:
		if self.editor.path:
			self.editor.checkSave()
			self.console.excute(self.editor.path)

	def console_switch(self, state: bool) -> None:
		self.menu_run_run.setEnabled(not state)
		self.menu_run_stop.setEnabled(state)

	def openFile(self) -> None:
		filename, _ = QFileDialog.getOpenFileName(self, caption="打开文件", filter='*.py')
		self.editor.setPath(Path(filename))

	def openDir(self) -> None:
		path = QFileDialog.getExistingDirectory(caption="打开文件夹")
		self.dirView.setPath(Path(path))

	def setup(self) -> None:
		self.setWindowTitle("Code")
		self.resize(1080, 720)
		self.setCentralWidget(QWidget(self))

		self.setup_win()
		self.setup_menu()
		self.setup_statusbar()
		self.setup_connect()

	def setup_win(self) -> None:
		centralwidget = self.centralWidget()
		centralwidget.setLayout(QGridLayout(centralwidget))
		layout = centralwidget.layout()

		self.splitter_h = QSplitter(Qt.Horizontal, centralwidget)
		self.dirView = DirView(self.splitter_h)
		self.splitter_v = QSplitter(Qt.Vertical, self.splitter_h)
		self.editor = Editor(self.splitter_v)
		self.console = Console(self.splitter_v)

		self.dirView.setMinimumSize(200, 0)
		self.editor.setHighlighter(PythonSyntax())
		self.console.setMinimumSize(0, 150)
		self.splitter_v.setSizes([720, 150])
		self.splitter_h.setSizes([200, 1080])
		sizePolicy = self.splitter_v.sizePolicy()
		sizePolicy.setHorizontalStretch(1)
		self.splitter_v.setSizePolicy(sizePolicy)

		layout.addWidget(self.splitter_h)

	def setup_menu(self) -> None:
		self.menu_file_openfile = QAction(text="打开文件", triggered=self.openFile, shortcut=QKeySequence.StandardKey.Open)
		self.menu_file_opendir = QAction(text="打开文件夹", triggered=self.openDir, shortcut="Ctrl+Alt+K")
		self.menu_file_save = QAction(text="保存", triggered=self.editor.save, shortcut=QKeySequence.StandardKey.Save)
		self.menu_file_saveAs = QAction(text="另存为", triggered=self.editor.saveAs, shortcut=QKeySequence.StandardKey.SaveAs)
		self.menu_edit_copy = QAction(text="复制", triggered=self.editor.copy, shortcut=QKeySequence.StandardKey.Copy)
		self.menu_edit_cut = QAction(text="剪切", triggered=self.editor.cut, shortcut=QKeySequence.StandardKey.Cut)
		self.menu_edit_paste = QAction(text="粘贴", triggered=self.editor.paste, shortcut=QKeySequence.StandardKey.Paste)
		self.menu_run_run = QAction(text="运行", triggered=self.console_run, shortcut="Shift+F")
		self.menu_run_stop = QAction(text="停止", triggered=self.console.stop, shortcut="Alt+Shift+F")

		menubar = self.menuBar()
		self.menu_file = QMenu(title="文件", parent=menubar)
		self.menu_edit = QMenu(title="编辑", parent=menubar)
		self.menu_run = QMenu(title="运行", parent=menubar)
		menubar.addAction(self.menu_file.menuAction())
		menubar.addAction(self.menu_edit.menuAction())
		menubar.addAction(self.menu_run.menuAction())
		self.setMenuBar(menubar)

		self.menu_file.addAction(self.menu_file_openfile)
		self.menu_file.addAction(self.menu_file_opendir)
		self.menu_file.addSeparator()
		self.menu_file.addAction(self.menu_file_save)
		self.menu_file.addAction(self.menu_file_saveAs)

		self.menu_edit.addAction(self.menu_edit_copy)
		self.menu_edit.addAction(self.menu_edit_cut)
		self.menu_edit.addAction(self.menu_edit_paste)

		self.menu_run.addAction(self.menu_run_run)
		self.menu_run.addAction(self.menu_run_stop)

	def setup_statusbar(self) -> None:
		# self.status_encoding = QLabel(text="UTF-8")
		#
		# statusbar = self.statusBar()
		# statusbar.setEnabled(True)
		# statusbar.addPermanentWidget(self.status_encoding)
		pass

	def setup_connect(self) -> None:
		self.menu_run_stop.setEnabled(False)
		self.console.stateChange.connect(self.console_switch)
		self.dirView.selectFile.connect(self.editor.setPath)
		self.editor.pathChange.connect(self.setWindowTitle)
