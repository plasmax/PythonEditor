from Qt import QtWidgets, QtGui, QtCore
import shortcuts
import linenumberarea

class Editor(QtWidgets.QPlainTextEdit):
    """
    Code Editor widget with 
    basic functionality and signals.
    """
    clearOutputSignal = QtCore.Signal()
    execTextSignal = QtCore.Signal(str, str)
    
    def __init__(self):
        super(Editor, self).__init__()
        shortcuts.installShortcuts(self)
        linenumberarea.LineNumberArea(self)
