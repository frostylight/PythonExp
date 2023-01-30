from pathlib import Path

from PySide6.QtCore import QProcess, Qt, Signal, SignalInstance
from PySide6.QtGui import QInputMethodEvent, QKeyEvent, QTextCursor
from PySide6.QtWidgets import QTextEdit, QWidget


class Console(QTextEdit):
	stateChanged: SignalInstance = Signal(bool)
	cursorPositionChanged: SignalInstance

	def __init__(self, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self.setAcceptRichText(False)
		self.process: QProcess | None = None
		self.__stop()
		self.cursorPositionChanged.connect(self.cursorCheck)
		self.__readOnly = False

	def append(self, text: str) -> None:
		textCursor = self.textCursor()
		textCursor.movePosition(QTextCursor.MoveOperation.End)
		self.setTextCursor(textCursor)
		self.insertPlainText(text)

	def cursorCheck(self) -> None:
		"""
		Only the last line can be edited
		"""
		cursor = self.textCursor()
		if cursor.block().blockNumber() == self.document().lastBlock().blockNumber():
			self.__readOnly = False
		else:
			self.__readOnly = True

	def __begin(self) -> None:
		self.clear()
		self.setReadOnly(False)
		self.stateChanged.emit(True)

	def __stop(self) -> None:
		self.setReadOnly(True)
		if self.process is not None:
			self.process.close()
			self.process = None
		self.stateChanged.emit(False)

	def inputMethodEvent(self, event: QInputMethodEvent) -> None:
		if self.__readOnly:
			event.ignore()
			return
		super().inputMethodEvent(event)

	def keyPressEvent(self, ev: QKeyEvent) -> None:
		print(f"keyPressed {ev.key()} {ev.text()}")
		if self.__readOnly and ev.text():
			ev.ignore()
			return
		if ev.key() == Qt.Key.Key_Backspace and (self.__readOnly or self.textCursor().atBlockStart()):  # unable to del line
			ev.ignore()
			return
		super().keyPressEvent(ev)
		if ev.key() == Qt.Key.Key_Enter or ev.key() == Qt.Key.Key_Return:  #send last line to process
			self.process_stdin(self.document().toPlainText().splitlines(keepends=True)[-1])

	def process_stdin(self, stdin: str) -> None:
		"""
		send message to process

		:param stdin: message to be sent
		"""
		if self.process is None:
			return
		self.process.write(stdin.encode("utf-8"))

	def process_stdout(self) -> None:
		"""
		receive stdout/stderror from process
		"""
		if self.process is None:
			return
		dataBytes = bytes(self.process.readAll())
		try:
			data = dataBytes.decode("utf-8")
			self.append(data)
		except UnicodeDecodeError:
			data = dataBytes.decode()
			self.append(data)

	def process_finish(self, exitCode: int, exitStatus: QProcess.ExitStatus) -> None:
		self.append(f"Process exit with code {exitCode}\nStatus : {exitStatus}\n")
		self.__stop()

	def execute(self, path: Path) -> None:
		self.__begin()
		if self.process is not None:
			self.process.close()
		else:
			self.process = QProcess()
		self.process.start("python", ["-X utf8", str(path)])
		self.append(f"python -X utf8 {path}\n")
		self.process.finished.connect(self.process_finish)
		self.process.readyReadStandardOutput.connect(self.process_stdout)
		self.process.readyReadStandardError.connect(self.process_stdout)

	def stop(self) -> None:
		self.__stop()
