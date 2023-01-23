from PySide6.QtCore import Qt, Signal, SignalInstance
from PySide6.QtGui import QCloseEvent, QFocusEvent, QFont, QFontMetricsF, QKeyEvent, QShowEvent, QWheelEvent
from PySide6.QtWidgets import QTextEdit, QWidget, QMessageBox
from pathlib import Path


class EditorTab(QTextEdit):
	# TODO save & saveAs & checkSave
	def __init__(self, parent: QWidget | None, path: Path) -> None:
		super().__init__(parent)
		self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
		self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
		self.setAcceptRichText(False)

		# TODO custom font & fontsize & ...
		self.setFont(QFont('Consola', pointSize=15))
		self.setTabWidth(4)

		self.__path = path
		self.__ctrlPressed = False
		self.__load()

	def __load(self) -> None:
		# TODO encoding & lazy
		self.setText(self.__path.read_text(encoding="utf-8"))

	def reload(self) -> None:
		if self.__path.is_file():
			self.__load()
		elif not self.document().isModified():
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
		# TODO check saved
		super().closeEvent(event)
