from Qt import QtWidgets, QtGui, QtCore

import shortcuts
import linenumberarea
import syntaxhighlighter

class Editor(QtWidgets.QPlainTextEdit):
    """
    Code Text Editor widget with 
    basic functionality.
    """

    def __init__(self):
        super(Editor, self).__init__()
        self.setObjectName('Editor')
        linenumberarea.LineNumberArea(self)
        syntaxhighlighter.Highlight(self.document())
        self.setTabStopWidth(4)
