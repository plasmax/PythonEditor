import uuid
from Qt import QtWidgets, QtGui, QtCore

import shortcuteditor
from features import (shortcuts, 
                      linenumberarea, 
                      syntaxhighlighter,
                      autocompletion,
                      contextmenu)

class Editor(QtWidgets.QPlainTextEdit):
    """
    Code Text Editor widget with 
    basic functionality.
    TODO: MouseWheelEvent + Ctrl == zoom in/out
    Home Key should jump to end of whitespace
    Ctrl+Shift+Delete for delete rest of line
    """
    tab_signal = QtCore.Signal()
    return_signal = QtCore.Signal()
    wrap_signal = QtCore.Signal(str)
    focus_in_signal = QtCore.Signal(QtGui.QFocusEvent)
    key_pressed_signal = QtCore.Signal(QtGui.QKeyEvent)
    post_key_pressed_signal = QtCore.Signal(QtGui.QKeyEvent)
    wheel_signal = QtCore.Signal(QtGui.QWheelEvent)
    context_menu_signal = QtCore.Signal(QtWidgets.QMenu)
    home_key_signal = QtCore.Signal()
    home_key_ctrl_alt_signal = QtCore.Signal()
    end_key_ctrl_alt_signal = QtCore.Signal()
    ctrl_x_signal = QtCore.Signal()
    ctrl_enter_signal = QtCore.Signal()

    relay_clear_output_signal = QtCore.Signal() 

    def __init__(self, handle_shortcuts=True):
        super(Editor, self).__init__()
        self.setObjectName('Editor')
        self.setAcceptDrops(True)
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
                            ] #for wrap_signal

        if handle_shortcuts:
            sch = shortcuts.ShortcutHandler(self, use_tabs=False)
            sch.clear_output_signal.connect(self.relay_clear_output_signal)
            self.shortcuteditor = shortcuteditor.ShortcutEditor(sch)
            
        self.uid = str(uuid.uuid4())

    @property
    def uid(self):
        return self._uid

    @uid.setter
    def uid(self, uid):
        self._uid = uid

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

        if (event.key() == QtCore.Qt.Key_Return
                and event.modifiers() == QtCore.Qt.ControlModifier):
            return self.ctrl_enter_signal.emit()

        if (event.text() in self.wrap_types
                and self.textCursor().hasSelection()):
            return self.wrap_signal.emit(event.text())

        if event.key() == QtCore.Qt.Key_Home:
            if event.modifiers() == QtCore.Qt.ControlModifier | QtCore.Qt.AltModifier:
                self.home_key_ctrl_alt_signal.emit()
            elif event.modifiers() == QtCore.Qt.NoModifier:
                return self.home_key_signal.emit()

        if (event.key() == QtCore.Qt.Key_End
                and event.modifiers() == QtCore.Qt.ControlModifier | QtCore.Qt.AltModifier):
            self.end_key_ctrl_alt_signal.emit()

        if (event.key() == QtCore.Qt.Key_X
                and event.modifiers() == QtCore.Qt.ControlModifier):
            self.ctrl_x_signal.emit()

        super(Editor, self).keyPressEvent(event)
        self.post_key_pressed_signal.emit(event)
        
    def keyReleaseEvent(self, event):
        self.wait_for_autocomplete = True
        super(Editor, self).keyReleaseEvent(event)

    def contextMenuEvent(self, event):
        """
        Creates a standard context menu
        and emits it for futher changes 
        and execution elsewhere.
        """
        menu = self.createStandardContextMenu()
        self.context_menu_signal.emit(menu)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls:
            e.accept()
        else:
            super(Editor, self).dragEnterEvent(e)
    
    def dragMoveEvent(self, e):
        if e.mimeData().hasUrls:
            e.accept()
        else:
            super(Editor, self).dragMoveEvent(e)

    def dropEvent(self, e):
        mimeData = e.mimeData()
        if (mimeData.hasUrls
                and mimeData.urls()):
            urls = mimeData.urls()

            text_list = []
            for url in urls:
                path = url.toLocalFile()
                with open(path, 'r') as f:
                    text_list.append(f.read())
                    
            self.textCursor().insertText('\n'.join(text_list))
        else:
            super(Editor, self).dropEvent(e)

    def wheelEvent(self, e):
        """
        Restore focus and emit signal if
        ctrl held.
        """
        self.setFocus(QtCore.Qt.MouseFocusReason)
        if (e.modifiers() == QtCore.Qt.ControlModifier
                and e.orientation() == QtCore.Qt.Orientation.Vertical):
            return self.wheel_signal.emit(e)
        super(Editor, self).wheelEvent(e)
       
