import os
from pathlib import Path
from typing import Any

from PySide6.QtCore import QModelIndex, QObject, QPersistentModelIndex, QPoint, QRegularExpression, QSortFilterProxyModel, Qt, Signal, SignalInstance
from PySide6.QtGui import QAction, QCursor
from PySide6.QtWidgets import QFileSystemModel, QLineEdit, QMenu, QMessageBox, QTreeView, QWidget, QInputDialog


class FileSystemModel(QFileSystemModel):
	def __init__(self, parent: QObject | None = None) -> None:
		super().__init__(parent)
		self.setOptions(QFileSystemModel.Option.DontResolveSymlinks | QFileSystemModel.Option.DontUseCustomDirectoryIcons)
		#self.setReadOnly(False)
		# self.setNameFilters(['*.py'])
		# self.setNameFilterDisables(False)
		pass

	def columnCount(self, parent: QModelIndex | QPersistentModelIndex = ...) -> int:
		return 1

	def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> Any:
		if section > 0 or orientation != Qt.Orientation.Horizontal or role != Qt.ItemDataRole.DisplayRole:
			return super().headerData(section, orientation, role)
		return self.rootPath()


class ExplorerModel(QSortFilterProxyModel):
	def __init__(self, parent: QObject | None = None) -> None:
		super().__init__(parent)
		self._model = FileSystemModel(self)
		self.setSourceModel(self._model)
		self.filter: list[QRegularExpression] = []

	def loadFilter(self, path: Path | str) -> None:
		self.filter.clear()
		path = Path(path).joinpath(".ignore")
		if not path.exists():
			return
		for pattern in path.read_text(encoding="utf-8").splitlines():
			self.filter.append(QRegularExpression(pattern))

	def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex | QPersistentModelIndex) -> bool:
		index = self._model.index(source_row, 0, source_parent)
		path = self._model.filePath(index)
		if not path.startswith(self._model.rootPath()) or path == self._model.rootPath():
			return True
		#print(self._model.rootPath(), path)
		name = self._model.fileName(index)
		for reg in self.filter:
			mt = reg.match(name)
			if mt.hasMatch():
				return False
		return True

	def setRootPath(self, path: str) -> QModelIndex:
		self.loadFilter(path)
		return self.mapFromSource(self._model.setRootPath(path))

	def filePath(self, index: QModelIndex) -> str:
		return self._model.filePath(self.mapToSource(index))

	def isDir(self, index: QModelIndex) -> bool:
		return self._model.isDir(self.mapToSource(index))


class PopMenu(QMenu):
	def __init__(self, parent: QWidget, path: str | Path | None = None) -> None:
		super().__init__(parent)
		self._rootPath = Path() if path is None else Path(path)
		self._path = self._rootPath
		self._input = QInputDialog(self)

		self.action_newfile = QAction(text="新建文件", triggered=self.createFile)
		self.action_newfolder = QAction(text="新建文件夹", triggered=self.createFolder)
		self.action_rename = QAction(text="重命名", triggered=self.rename)
		self.action_remove = QAction(text="彻底删除", triggered=self.remove)
		self.loadAction()

	def loadAction(self) -> None:
		self.addAction(self.action_newfile)
		self.addAction(self.action_newfolder)
		self.addSeparator()
		self.addAction(self.action_rename)
		self.addSeparator()
		self.addAction(self.action_remove)

	def setPath(self, path: str | Path | None) -> None:
		self._path = self._rootPath if path is None else Path(path)
		self.action_newfile.setVisible(self._path.is_dir())
		self.action_newfolder.setVisible(self._path.is_dir())
		self.action_rename.setVisible(not self._path.samefile(self._rootPath))
		self.action_remove.setVisible(not self._path.samefile(self._rootPath))

	def setRootPath(self, path: Path) -> None:
		self._rootPath = path

	def createFile(self) -> None:
		text, ret = self._input.getText(self, "新建文件", "输入文件名", QLineEdit.EchoMode.Normal)
		if not ret or not text:
			return
		path = self._path.joinpath(text)
		if path.exists() and path.is_file():
			QMessageBox.warning(self, "", "文件已存在")
			return
		try:
			path.open("w+").close()
		except PermissionError as e:
			QMessageBox.warning(self, "", f"无法访问\n{e}")
		except OSError as e:
			QMessageBox.warning(self, "", f"文件名不合法\n{e}")

	def createFolder(self) -> None:
		text, ret = self._input.getText(self, "新建文件夹", "输入路径名", QLineEdit.EchoMode.Normal)
		if not ret or not text:
			return
		path = self._path.joinpath(text)
		if path.exists() and path.is_dir():
			QMessageBox.warning(self, "", "文件夹已存在")
			return
		try:
			path.mkdir(parents=True)
		except PermissionError as e:
			QMessageBox.warning(self, "", f"无法访问\n{e}")
		except OSError as e:
			QMessageBox.warning(self, "", f"路径名不合法\n{e}")

	def rename(self) -> None:
		text, ret = self._input.getText(self, f"重命名{self._path.name}", "输入新名字", QLineEdit.EchoMode.Normal)
		if not ret or not text:
			return
		path = self._path.with_name(text)
		if path.exists() and ((path.is_dir() and self._path.is_dir()) or (path.is_file() and self._path.is_file())):
			QMessageBox.warning(self, "", "文件（夹）已存在")
			return
		try:
			self._path.rename(text)
		except PermissionError as e:
			QMessageBox.warning(self, "", f"无法访问\n{e}")
		except OSError as e:
			QMessageBox.warning(self, "", f"路径名不合法\n{e}")

	def remove(self) -> None:
		ret = QMessageBox.warning(self, "删除文件", f"确实要永久性删除此文件{'夹' if self._path.is_dir() else ''}吗？\n{self._path}",
								  QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
		if ret == QMessageBox.StandardButton.No:
			return
		try:
			os.remove(self._path)
		except PermissionError as e:
			QMessageBox.warning(self, "", f"无法访问\n{e}")


class Explorer(QTreeView):
	selectFile: SignalInstance = Signal(Path)
	clicked: SignalInstance
	customContextMenuRequested: SignalInstance

	def __init__(self, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self._model = ExplorerModel(self)
		self._path = Path()
		self._popMenu: PopMenu = PopMenu(self)
		self.setModel(self._model)
		self.setPath(self._path)

		self.setExpandsOnDoubleClick(False)
		self.clicked.connect(self.clickExpand)
		self.customContextMenuRequested.connect(self.contextMenu)
		self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

	def contextMenu(self, pos: QPoint) -> None:
		index = self.indexAt(pos)
		if not index.isValid():
			self._popMenu.setPath(None)
		else:
			self._popMenu.setPath(self._model.filePath(index))
		self._popMenu.exec(QCursor.pos())

	def clickExpand(self, index: QModelIndex) -> None:
		if self._model.isDir(index):
			self.setExpanded(index, not self.isExpanded(index))
		else:
			path = self._model.filePath(index)
			if path.endswith(".py"):
				self.selectFile.emit(Path(path))

	def setPath(self, path: Path | str = '.') -> None:
		tmp = Path(path)
		if not tmp.exists() or not tmp.is_dir():
			return
		self._path = tmp.resolve()
		self.setRootIndex(self._model.setRootPath(str(self._path)))
		self._popMenu.setRootPath(self._path)
