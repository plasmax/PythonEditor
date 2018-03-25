import sys

from Qt import QtWidgets, QtCore, QtGui
from editor import Editor
from terminal import Terminal
from shortcuts import ShortcutHandler
from codeeditor.core import execute

class IDE(QtWidgets.QWidget):
    """
    Main widget. 
    Sets up layout and connects 
    some signals.
    """
    def __init__(self):
        super(IDE, self).__init__()
        self.setObjectName('IDE')

        #construct layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setObjectName('IDE_MainLayout')
        layout.setContentsMargins(0,0,0,0)
        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        splitter.setObjectName('IDE_MainVerticalSplitter')

        self.editor = Editor()
        terminal = Terminal()
        splitter.addWidget(terminal)
        splitter.addWidget(self.editor)

        layout.addWidget(splitter)

        #connect signals
        sch = ShortcutHandler(self.editor)
        sch.execTextSignal.connect(execute.mainexec)
        sch.execTextSignal.connect(terminal.setTabFocus)
        sch.clearOutputSignal.connect(terminal.clear)
