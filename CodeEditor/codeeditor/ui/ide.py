import sys

from Qt import QtWidgets, QtCore, QtGui
from editor import Editor
from terminal import Terminal
from ..utils import execute

class IDE(QtWidgets.QWidget):
    """
    Main widget. Sets up layout and connects signals.
    """
    def __init__(self):
        super(IDE, self).__init__()

        #construct layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)

        self.editor = Editor()
        terminal = Terminal()
        splitter.addWidget(terminal)
        splitter.addWidget(self.editor)

        layout.addWidget(splitter)

        #connect signals
        self.editor.execTextSignal.connect(execute.mainexec)
        self.editor.execTextSignal.connect(terminal.setTabFocus)
        self.editor.clearOutputSignal.connect(terminal.clear)
