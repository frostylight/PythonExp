from pathlib import Path

from PySide6.QtCore import QProcess, Qt, Signal, SignalInstance
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QTextEdit, QWidget


class Console(QTextEdit):
	stateChange: SignalInstance = Signal(bool)

	def __init__(self, parent: QWidget | None = None) -> None:
		super().__init__(parent)
		self.setAcceptRichText(False)
		self.process: QProcess | None = None
		self.disable()
		self.cursorPositionChanged.connect(self.cursorCheck)

	def cursorCheck(self) -> None:
		"""
		Only the last line can be edited
		"""
		cursor = self.textCursor()
		if cursor.block().blockNumber() == self.document().lastBlock().blockNumber():
			self.setReadOnly(False)
		else:
			self.setReadOnly(True)

	def disable(self) -> None:
		# TODO to be polished
		self.setReadOnly(True)
		if self.process is not None:
			self.process.close()
			self.process = None
		self.stateChange.emit(False)

	def keyPressEvent(self, ev: QKeyEvent) -> None:
		if ev.key() == Qt.Key.Key_Backspace:  # unable to del line
			if self.textCursor().atBlockStart():
				ev.ignore()
			else:
				super().keyPressEvent(ev)
		elif ev.key() == Qt.Key.Key_Enter or ev.key() == Qt.Key.Key_Return:  #send last line to process
			super().keyPressEvent(ev)
			self.process_stdin(self.document().toPlainText().splitlines(keepends=True)[-1])
		else:
			super().keyPressEvent(ev)

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
		#print("stdout:", dataBytes)
		try:
			data = dataBytes.decode("utf-8")
			self.insertPlainText(data)
		except UnicodeDecodeError:
			data = dataBytes.decode()
			self.insertPlainText(data)

	def process_finish(self, exitCode: int, exitStatus: QProcess.ExitStatus) -> None:
		self.insertPlainText(f"Process exit with code {exitCode}\nStatus : {exitStatus}\n")
		self.disable()

	def execute(self, path: Path) -> None:
		self.clear()
		self.setReadOnly(False)
		self.stateChange.emit(True)
		if self.process is not None:
			self.process.close()
		else:
			self.process = QProcess()
		self.process.start("python", ["-X utf8", str(path)])
		self.insertPlainText(f"python -X utf8 {path}\n")
		self.process.finished.connect(self.process_finish)
		self.process.readyReadStandardOutput.connect(self.process_stdout)
		self.process.readyReadStandardError.connect(self.process_stdout)

	def stop(self) -> None:
		self.disable()
