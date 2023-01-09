import keyword
import builtins

from PySide6.QtGui import QCursor, QSyntaxHighlighter, QTextCharFormat, QTextDocument, QColor
from PySide6.QtCore import QRegularExpression, Qt

from PySide6.QtWidgets import QApplication


class SyntaxRule:
	"""
	Syntax highlighter rule and format
	"""

	def __init__(self, rule: QRegularExpression | None = None, reg: str | None = None, fmt: QTextCharFormat | None = None, color: Qt.GlobalColor | QColor | None = None,
				 italic: bool = False) -> None:
		"""
		reg >(cover) rule
		color / italic >(cover) format

		:param rule: regular expression
		:param reg: regular expression string
		:param fmt: format of text
		:param color: color of text
		:param italic: whether the text should be italic
		"""
		self.rule: QRegularExpression = rule if rule is not None else QRegularExpression()
		self.format: QTextCharFormat = fmt if fmt is not None else QTextCharFormat()
		if reg is not None:
			self.rule.setPattern(reg)
		if color is not None:
			self.format.setForeground(color)
		if italic:
			self.format.setFontItalic(True)


class PythonSyntax(QSyntaxHighlighter):
	"""
	Highlighter of Python code
	"""

	def __init__(self, parent: QTextDocument | None = None) -> None:
		super().__init__(parent)
		self.rule: list[SyntaxRule] = []
		self.setup_rule()

	def setup_rule(self) -> None:
		#builtins
		self.rule.append(SyntaxRule(reg="|".join([r'\b(?<!\.){}\b'.format(bi) for bi in builtins.__dir__()]), color=Qt.GlobalColor.blue))
		# keyword
		self.rule.append(SyntaxRule(reg="|".join([r'\b(?<!\.){}\b'.format(kw) for kw in keyword.kwlist] + [r'\bself\b']), color=Qt.GlobalColor.darkMagenta))
		# magic function
		self.rule.append(SyntaxRule(reg=r"\b__[a-zA-Z][\da-zA-Z]*__", color=Qt.GlobalColor.magenta))
		# const number
		self.rule.append(
			SyntaxRule(reg="|".join([r'\b[0]+\b', r'\b[1-9]+\d+\b', r'\b0[bB][01]+\b', r'\b0[oO][0-7]+\b', r'\b0[xX][\da-fA-F]+\b']), color=Qt.GlobalColor.darkCyan))
		# const string
		self.rule.append(SyntaxRule(reg=r'"[^"]*?"' + r"|'[^']*?'", color=Qt.GlobalColor.darkGreen))
		# comment
		self.rule.append(SyntaxRule(reg=r'^\s*#.*', color=Qt.GlobalColor.gray, italic=True))

	def highlightBlock(self, text: str) -> None:
		for rl in self.rule:
			i = rl.rule.globalMatch(text)
			while i.hasNext():
				mt = i.next()
				self.setFormat(mt.capturedStart(), mt.capturedLength(), rl.format)

	def rehighlight(self) -> None:
		QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
		QSyntaxHighlighter.rehighlight(self)
		QApplication.restoreOverrideCursor()
