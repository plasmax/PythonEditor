from Qt import QtWidgets, QtGui, QtCore

from features import (shortcuts, 
                      linenumberarea, 
                      syntaxhighlighter,
                      autocompletion,
                      contextmenu)

class Editor(QtWidgets.QPlainTextEdit):
    """
    Code Text Editor widget with 
    basic functionality.
    """
    tab_signal = QtCore.Signal()
    return_signal = QtCore.Signal()
    wrap_signal = QtCore.Signal(str)
    focus_in_signal = QtCore.Signal(QtGui.QFocusEvent)
    key_pressed_signal = QtCore.Signal(QtGui.QKeyEvent)
    post_key_pressed_signal = QtCore.Signal(QtGui.QKeyEvent)
    context_menu_signal = QtCore.Signal(QtWidgets.QMenu)

    def __init__(self):
        super(Editor, self).__init__()
        self.setObjectName('Editor')
        linenumberarea.LineNumberArea(self)
        syntaxhighlighter.Highlight(self.document())
        self.contextmenu = contextmenu.ContextMenu(self)

        self.wait_for_autocomplete = True
        self.autocomplete = autocompletion.AutoCompleter(self)
        self.wrap_types = [
                            '\'', '"',
                            '[', ']',
                            '(', ')',
                            '{', '}'
                            '<', '>'
                            ]

    def focusInEvent(self, event):
        self.focus_in_signal.emit(event)
        super(Editor, self).focusInEvent(event)

    def keyPressEvent(self, event):
        """ 
        Emit signals for key events
        that QShortcut cannot override.
        """
        if self.wait_for_autocomplete:
            self.key_pressed_signal.emit(event)
            return 

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
        self.post_key_pressed_signal.emit(event)

    def contextMenuEvent(self, event):
        """
        Creates a standard context menu
        and emits it for futher changes 
        and execution elsewhere.
        """
        menu = self.createStandardContextMenu()
        self.context_menu_signal.emit(menu)

