import uuid
from PythonEditor.ui.Qt import QtWidgets, QtGui, QtCore

from PythonEditor.utils.constants import DEFAULT_FONT
from PythonEditor.ui.dialogs import shortcuteditor
from PythonEditor.ui.features import (shortcuts,
                                      linenumberarea,
                                      syntaxhighlighter,
                                      autocompletion,
                                      contextmenu)

CTRL = QtCore.Qt.ControlModifier
CTRL_ALT = QtCore.Qt.ControlModifier | QtCore.Qt.AltModifier


class Editor(QtWidgets.QPlainTextEdit):
    """
    Code Editor widget. Extends QPlainTextEdit to provide:
    - Line Number Area
    - Syntax Highlighting
    - Autocompletion (of Python code)
    - Shortcuts for code editing
    - New Context Menu
    - Signals for connecting the Editor to other UI elements.
    - Unique identifier to match Editor widget to file storage.
    """
    wrap_types = ['\'', '"',
                  '[', ']',
                  '(', ')',
                  '{', '}',
                  '<', '>']

    tab_signal = QtCore.Signal()
    return_signal = QtCore.Signal(QtGui.QKeyEvent)
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
    ctrl_n_signal = QtCore.Signal()
    ctrl_w_signal = QtCore.Signal()
    ctrl_enter_signal = QtCore.Signal()
    contents_saved_signal = QtCore.Signal(object)
    read_only_signal = QtCore.Signal(bool)

    relay_clear_output_signal = QtCore.Signal()
    editingFinished = QtCore.Signal()

    def __init__(self, handle_shortcuts=True, uid=None):
        super(Editor, self).__init__()
        self.setObjectName('Editor')
        self.setAcceptDrops(True)
        font = QtGui.QFont(DEFAULT_FONT)
        font.setPointSize(10)
        self.setFont(font)

        self._changed = False
        self.textChanged.connect(self._handle_text_changed)

        linenumberarea.LineNumberArea(self)
        syntaxhighlighter.Highlight(self.document())
        self.contextmenu = contextmenu.ContextMenu(self)

        self.wait_for_autocomplete = True
        # TOOD: add a new autocompleter that uses DirectConnection.
        self.autocomplete = autocompletion.AutoCompleter(self)

        if handle_shortcuts:
            sch = shortcuts.ShortcutHandler(self, use_tabs=False)
            sch.clear_output_signal.connect(self.relay_clear_output_signal)
            self.shortcuteditor = shortcuteditor.ShortcutEditor(sch)

        if uid is None:
            uid = str(uuid.uuid4())
        self._uid = uid

        self.selectionChanged.connect(self.highlight_same_words)
        self.modificationChanged.connect(self._handle_modificationChanged)
        self._read_only = False

    @property
    def uid(self):
        """
        Unique identifier for keeping track of
        document and editor changes in autosave files.
        """
        return self._uid

    @uid.setter
    def uid(self, uid):
        self._uid = uid

    @property
    def name(self):
        """
        The name for the editor document.
        Generally corresponds to a tab name and/or
        file name.
        """
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def path(self):
        """
        A path to a file where the document
        expects to be saved.
        """
        return self._path

    @path.setter
    def path(self, path):
        self._path = path

    @property
    def read_only(self):
        """
        Returns True or False,
        determining whether the editor is in
        read-only mode or not. Should be disabled
        when editing has begun.
        TODO: is the existing readOnly property good enough for this?
        """
        return self._read_only

    @read_only.setter
    def read_only(self, state=False):
        # TODO: set an indicator (italic text in sublime)
        # to denote state
        self._read_only = state
        self.read_only_signal.emit(state)

    @QtCore.Slot(bool)
    def _handle_modificationChanged(self, changed):
        self.read_only = not changed

    def _handle_text_changed(self):
        self._changed = True

    def setTextChanged(self, state=True):
        self._changed = state

    def highlight_same_words(self):
        """
        Highlights other matching words in document
        when full word selected.
        TODO: implement this!
        """
        textCursor = self.textCursor()
        if not textCursor.hasSelection():
            return

        # text = textCursor.selection().toPlainText()
        # textCursor.select(QtGui.QTextCursor.WordUnderCursor)
        # word = textCursor.selection().toPlainText()
        # print(text, word)
        # if text == word:
            # print(word)

    def focusInEvent(self, event):
        self.focus_in_signal.emit(event)
        super(Editor, self).focusInEvent(event)

    def focusOutEvent(self, event):
        if self._changed:
            self.editingFinished.emit()
        super(Editor, self).focusOutEvent(event)

    def keyPressEvent(self, event):
        """
        Emit signals for key events
        that QShortcut cannot override.
        """
        # will this be enough to give focus back to the
        # script editor or rest of the application?
        if not self.hasFocus():
            event.ignore()
            return

        if self.wait_for_autocomplete:
            # TODO: Connect (in autocomplete) using
            # QtCore.Qt.DirectConnection to work synchronously
            self.key_pressed_signal.emit(event)
            return

        if event.modifiers() == QtCore.Qt.NoModifier:
            # Tab Key
            if event.key() == QtCore.Qt.Key_Tab:
                return self.tab_signal.emit()
            # Enter/Return Key
            if event.key() == QtCore.Qt.Key_Return:
                return self.return_signal.emit(event)

        # Ctrl+Enter/Return Key
        if (event.key() == QtCore.Qt.Key_Return
                and event.modifiers() == CTRL):
            return self.ctrl_enter_signal.emit()

        # Surround selected text in brackets or quotes
        if (event.text() in self.wrap_types
                and self.textCursor().hasSelection()):
            return self.wrap_signal.emit(event.text())

        if event.key() == QtCore.Qt.Key_Home:
            # Ctrl+Alt+Home
            if event.modifiers() == CTRL_ALT:
                self.home_key_ctrl_alt_signal.emit()
            # Home
            elif event.modifiers() == QtCore.Qt.NoModifier:
                return self.home_key_signal.emit()

        # Ctrl+Alt+End
        if (event.key() == QtCore.Qt.Key_End
                and event.modifiers() == CTRL_ALT):
            self.end_key_ctrl_alt_signal.emit()

        # Ctrl+X
        if (event.key() == QtCore.Qt.Key_X
                and event.modifiers() == CTRL):
            self.ctrl_x_signal.emit()

        # Ctrl+X
        if (event.key() == QtCore.Qt.Key_N
                and event.modifiers() == CTRL):
            self.ctrl_n_signal.emit()

        # Ctrl+W
        if (event.key() == QtCore.Qt.Key_W
                and event.modifiers() == CTRL):
            self.ctrl_w_signal.emit()

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
        mimeData = e.mimeData()
        if mimeData.hasUrls:
            e.accept()
        else:
            super(Editor, self).dragEnterEvent(e)

        # prevent mimedata from being displayed unless alt is held
        app = QtWidgets.QApplication.instance()
        if app.keyboardModifiers() != QtCore.Qt.AltModifier:
            return

        # let's see what the data contains, at least!
        # maybe restrict this to non-known formats...
        for f in mimeData.formats():
            data = str(mimeData.data(f)).replace(b'\0', b'')
            data = data.replace(b'\x12', b'')
            print(f, data)

    def dragMoveEvent(self, e):
        # prevent mimedata from being displayed unless alt is held
        app = QtWidgets.QApplication.instance()
        if app.keyboardModifiers() != QtCore.Qt.AltModifier:
            super(Editor, self).dragMoveEvent(e)
            return

        if e.mimeData().hasUrls:
            e.accept()
        else:
            super(Editor, self).dragMoveEvent(e)

    def dropEvent(self, e):
        """
        TODO: e.ignore() files and send to edittabs to
        create new tab instead?
        """
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
        Restore focus and emit signal if ctrl held.
        """
        self.setFocus(QtCore.Qt.MouseFocusReason)
        if (e.modifiers() == CTRL
                and e.orientation() == QtCore.Qt.Orientation.Vertical):
            return self.wheel_signal.emit(e)
        super(Editor, self).wheelEvent(e)
