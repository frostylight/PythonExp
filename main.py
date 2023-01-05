import sys

from PySide6.QtWidgets import QApplication

from ui import Ui_Main


class MainWindow(Ui_Main):
	def __init__(self) -> None:
		super().__init__()


if __name__ == '__main__':
	app = QApplication(sys.argv)
	mainwin = MainWindow()
	mainwin.show()
	sys.exit(app.exec())
