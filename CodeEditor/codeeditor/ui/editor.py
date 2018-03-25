from Qt import QtWidgets, QtGui, QtCore

import shortcuts
import linenumberarea
import syntaxhighlighter

class Editor(QtWidgets.QPlainTextEdit):
    """
    Code Text Editor widget with 
    basic functionality.
    """
    tab_signal = QtCore.Signal()
    return_signal = QtCore.Signal()
    wrap_signal = QtCore.Signal(str)

    def __init__(self):
        super(Editor, self).__init__()
        self.setObjectName('Editor')
        linenumberarea.LineNumberArea(self)
        syntaxhighlighter.Highlight(self.document())
        self.wrap_types = [
                            '\'', '"',
                            '[', ']',
                            '(', ')',
                            '{', '}'
                            '<', '>'
                            ]

    def keyPressEvent(self, event):
        """ 
        Emit signals for key events
        that QShortcut cannot override.
        """
        if event.modifiers() == QtCore.Qt.NoModifier:
            if event.key() == QtCore.Qt.Key_Tab:
                return self.tab_signal.emit()
            if event.key() == QtCore.Qt.Key_Return:
                return self.return_signal.emit()

        if (event.text() in self.wrap_types
                and self.textCursor().hasSelection()):
            return self.wrap_signal.emit(event.text())

        if (event.key() == QtCore.Qt.Key_Home
                and event.modifiers() == QtCore.Qt.ControlModifier | QtCore.Qt.AltModifier):
            raise NotImplementedError, 'add move line to top function'

        super(Editor, self).keyPressEvent(event)

