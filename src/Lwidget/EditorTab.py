from PySide6.QtCore import Qt, Signal, SignalInstance
from PySide6.QtGui import QCloseEvent, QFocusEvent, QFontMetricsF, QKeyEvent, QWheelEvent
from PySide6.QtWidgets import QTextEdit, QWidget
from pathlib import Path


class EditorTab(QTextEdit):
	def __init__(self, parent: QWidget | None, path: Path) -> None:
		super().__init__(parent)
		self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
		self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
		self.setAcceptRichText(False)

		self.__path = path
		self.__ctrlPressed = False

	def setTabWidth(self, tabWidth: int) -> None:
		self.setTabStopDistance(QFontMetricsF(self.font()).horizontalAdvance(' ') * tabWidth)

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
		else:
			super().wheelEvent(event)

	def closeEvent(self, event: QCloseEvent) -> None:
		super().closeEvent(event)
