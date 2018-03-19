from Qt import QtWidgets, QtGui, QtCore
import shortcuts

class Editor(QtWidgets.QPlainTextEdit):
    """
    Code Editor widget with 
    basic functionality and signals.
    """
    execTextSignal = QtCore.Signal(str)

    def __init__(self):
        super(Editor, self).__init__()
        shortcuts.installShortcuts(self)
