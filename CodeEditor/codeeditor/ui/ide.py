import sys

from Qt import QtWidgets, QtCore, QtGui
from editor import Editor
from ..utils import execute

class IDE(QtWidgets.QWidget):
    """
    Main widget. Sets up layout and connects signals.
    """
    def __init__(self):
        super(IDE, self).__init__()
        layout = QtWidgets.QHBoxLayout(self)
        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        layout.addWidget(splitter)

        self.editor = Editor()
        splitter.addWidget(self.editor)

        #connect signals
        self.editor.execTextSignal.connect(execute.mainexec)
