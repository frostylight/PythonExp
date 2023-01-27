from PySide6.QtCore import Qt, Signal, SignalInstance
from PySide6.QtGui import QCloseEvent, QFocusEvent, QFont, QFontMetricsF, QKeyEvent, QShowEvent, QWheelEvent
from PySide6.QtWidgets import QFileDialog, QTextEdit, QWidget, QMessageBox
from pathlib import Path


class EditorTab(QTextEdit):
	titleChanged: SignalInstance = Signal(QWidget, str)

	def __init__(self, parent: QWidget | None, path: Path | None) -> None:
		super().__init__(parent)
		self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
		self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
		self.setAcceptRichText(False)

		# TODO custom font & fontsize & ...
		self.setFont(QFont('Consola', pointSize=15))
		self.setTabWidth(4)

		self.__path = path
		self.__ctrlPressed = False
		if self.__path:
			self.__load()

	@property
	def __title(self) -> str:
		# TODO custom style
		return self.__path.name if self.__path is not None else ""

	@property
	def path(self) -> Path:
		return self.__path

	def refreshTitle(self) -> None:
		self.titleChanged.emit(self, self.__title)

	def __save(self) -> None:
		# TODO custom | detect encoding
		self.__path.write_text(self.toPlainText(), encoding="utf-8")
		self.document().setModified(False)

	def saveAs(self) -> bool:
		filename, _ = QFileDialog.getSaveFileName(self, "保存为")
		if not filename:
			return False
		if self.__path is None:
			self.__path = Path(filename)
			self.__save()
			self.refreshTitle()
		else:
			path = Path(filename)
			path.write_text(self.toPlainText(), encoding="utf-8")
		return True

	def save(self) -> bool:
		if self.__path is None:
			return self.saveAs()
		self.__save()
		return True

	def checkSave(self) -> bool:
		if not self.document().isModified():
			return True
		ret = QMessageBox.warning(self, self.__title, "文件修改未保存。保存修改内容？",
								  QMessageBox.StandardButton.Save | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
		if ret == QMessageBox.StandardButton.Save:
			return self.save()
		elif ret == QMessageBox.StandardButton.No:
			return True
		return False

	def __load(self) -> None:
		# TODO custom encoding & lazy loading
		self.setText(self.__path.read_text(encoding="utf-8"))
		self.document().setModified(False)

	def reload(self) -> None:
		if self.__path is None or self.document().isModified():
			return
		if self.__path.is_file():
			self.__load()
		else:
			result = QMessageBox.warning(self, "保留文件", f"文件 {self.__path.resolve()} 不在了。\n是否在编辑器里保留它？",
										 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
			if result == QMessageBox.StandardButton.Yes:
				self.document().setModified(True)

	def setTabWidth(self, tabWidth: int) -> None:
		self.setTabStopDistance(QFontMetricsF(self.font()).horizontalAdvance(' ') * tabWidth)

	def showEvent(self, event: QShowEvent) -> None:
		self.reload()
		super().showEvent(event)

	def keyPressEvent(self, event: QKeyEvent) -> None:
		if event.key() == Qt.Key.Key_Control:
			self.__ctrlPressed = True
		super().keyPressEvent(event)

	def keyReleaseEvent(self, event: QKeyEvent) -> None:
		if event.key() == Qt.Key.Key_Control:
			self.__ctrlPressed = False
		super().keyReleaseEvent(event)

	def focusOutEvent(self, event: QFocusEvent) -> None:
		self.__ctrlPressed = False
		super().focusOutEvent(event)

	def wheelEvent(self, event: QWheelEvent) -> None:
		if self.__ctrlPressed:
			if event.angleDelta().y() > 0:
				self.zoomIn()
			else:
				self.zoomOut()
			event.ignore()
		else:
			super().wheelEvent(event)

	def closeEvent(self, event: QCloseEvent) -> None:
		if not self.checkSave():
			event.ignore()
		else:
			super().closeEvent(event)
