from PySide6.QtCore import Qt, Signal, SignalInstance
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QFocusEvent, QFont, QFontMetricsF, QKeyEvent, QWheelEvent, QSyntaxHighlighter
from PySide6.QtWidgets import QApplication, QFileDialog, QTextEdit, QWidget, QMessageBox

from pathlib import Path


class Editor(QTextEdit):
	pathChange: SignalInstance = Signal(str)

	def __init__(self, parent: QWidget | None = None, tabWidth: int = 4, highlighter: QSyntaxHighlighter | None = None) -> None:
		super().__init__(parent)
		self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
		self.setAcceptDrops(True)
		self.setFont(QFont('Consola', pointSize=15))
		self.setTabWidth(tabWidth)
		self.setAcceptRichText(False)

		self.ctrlPressed = False
		self.path: Path | None = None
		self.highlighter: QSyntaxHighlighter | None = None
		if highlighter is not None:
			self.setHighlighter(highlighter)

	#self.document().find()

	def setHighlighter(self, highlighter: QSyntaxHighlighter) -> None:
		highlighter.setDocument(self.document())
		self.highlighter = highlighter

	def setTabWidth(self, tabWidth: int) -> None:
		self.setTabStopDistance(QFontMetricsF(self.font()).horizontalAdvance(' ') * tabWidth)

	def keyPressEvent(self, ev: QKeyEvent) -> None:
		if ev.key() == Qt.Key.Key_Control:
			self.ctrlPressed = True
		super().keyPressEvent(ev)

	def keyReleaseEvent(self, ev: QKeyEvent) -> None:
		if ev.key() == Qt.Key.Key_Control:
			self.ctrlPressed = False
		super().keyReleaseEvent(ev)

	def focusOutEvent(self, ev: QFocusEvent) -> None:
		self.ctrlPressed = False
		super().focusOutEvent(ev)

	def wheelEvent(self, ev: QWheelEvent) -> None:
		if self.ctrlPressed:
			if ev.angleDelta().y() > 0:
				self.zoomIn()
			else:
				self.zoomOut()
			ev.ignore()
		else:
			super().wheelEvent(ev)

	def dragEnterEvent(self, ev: QDragEnterEvent) -> None:
		if ev.mimeData().hasText() and ev.mimeData().text().startswith("file:") and ev.mimeData().text().lower().endswith('.py'):
			#print(ev.mimeData().text())
			ev.accept()
		else:
			ev.ignore()

	def dropEvent(self, ev: QDropEvent) -> None:
		file = Path(ev.mimeData().text()[8:])
		if not file.exists() or not file.is_file():
			ev.ignore()
			return
		self.setPath(file)

	def saveFile(self, filepath: Path) -> bool:
		with QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor):
			try:
				filepath.write_text(self.toPlainText(), encoding="utf-8")
			except Exception as e:
				QMessageBox.warning(self, "", f"打开文件{self.path}时出错\n{e}")
				return False
		self.loadFile()
		return True

	def loadFile(self, filepath: Path | None = None, encoding: str = "utf-8") -> None:
		if filepath is not None:
			self.path = filepath
		if self.path:
			self.setText(self.path.read_text(encoding))

	def save(self) -> bool:
		if self.path is None:
			return self.saveAs()
		return self.saveFile(self.path)

	def saveAs(self) -> bool:
		filename, _ = QFileDialog.getSaveFileName(self, "保存为")
		if filename:
			self.path = Path(filename)
			return self.saveFile(self.path)
		else:
			return False

	def checkSave(self) -> bool:
		if self.document().isModified():
			ret = QMessageBox.warning(self, self.path.name if self.path is not None else "", "文件已被修改。保存修改内容？",
									  QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Cancel)
			if ret == QMessageBox.StandardButton.Save:
				return self.save()
			else:
				return False
		return True

	def setPath(self, path: Path, encoding='utf-8') -> None:
		self.checkSave()
		self.path = path.resolve()
		self.loadFile(path, encoding)
		self.pathChange.emit(str(path))
