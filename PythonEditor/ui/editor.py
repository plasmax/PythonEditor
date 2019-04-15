"""
This module contains the main text editor that can be
run independently, embedded in other layouts, or used
within the tabbed editor to have different contents
per tab.
"""

import os
import uuid
import __main__
from PythonEditor.ui.Qt import QtWidgets
from PythonEditor.ui.Qt import QtGui
from PythonEditor.ui.Qt import QtCore

from PythonEditor.utils import constants
from PythonEditor.ui.dialogs import shortcuteditor
from PythonEditor.ui.features import actions
from PythonEditor.ui.features import shortcuts
from PythonEditor.ui.features import linenumberarea
from PythonEditor.ui.features import syntaxhighlighter
from PythonEditor.ui.features import autocompletion
from PythonEditor.ui.features import contextmenu


class Editor(QtWidgets.QPlainTextEdit):
    """
    Code Editor widget. Extends QPlainTextEdit to
    provide (through separate modules):
    - Line Number Area
    - Syntax Highlighting
    - Autocompletion (of Python code)
    - Shortcuts for code editing
    - Custom Context Menu
    - Signals for connecting the Editor to other
        UI elements.
    """
    wrap_types = [
        '\'', '"',
        '[', ']',
        '(', ')',
        '{', '}',
    ]

    S = QtCore.Signal
    wrap_signal               = S(str)
    uuid_signal               = S(str)
    return_signal             = S(QtGui.QKeyEvent)
    focus_in_signal           = S(QtGui.QFocusEvent)
    focus_out_signal          = S(QtGui.QFocusEvent)
    post_key_pressed_signal   = S(QtGui.QKeyEvent)
    wheel_signal              = S(QtGui.QWheelEvent)
    key_pressed_signal        = S(QtGui.QKeyEvent)
    shortcut_signal           = S(QtGui.QKeyEvent)
    resize_signal             = S(QtGui.QResizeEvent)
    context_menu_signal       = S(QtWidgets.QMenu)
    tab_signal                = S()
    home_key_signal           = S()
    relay_clear_output_signal = S()
    editingFinished           = S()
    text_changed_signal       = S()

    def __init__(
            self,
            parent=None,
            handle_shortcuts=True,
            uid=None,
            init_features=True
        ):
        super(Editor, self).__init__(parent)
        self.setObjectName('Editor')
        self.setAcceptDrops(True)

        DEFAULT_FONT = constants.DEFAULT_FONT
        df = 'PYTHONEDITOR_DEFAULT_FONT'
        if os.getenv(df) is not None:
            DEFAULT_FONT = os.environ[df]
        font = QtGui.QFont(DEFAULT_FONT)
        font.setPointSize(10)
        self.setFont(font)
        self.setMouseTracking(True)
        self.setCursorWidth(2)
        self.setStyleSheet("""
        QToolTip {
        color: #F6F6F6;
        background-color: rgb(45, 42, 46);
        }
        """)

        # instance variables
        if uid is None:
            uid = str(uuid.uuid4())
        self._uuid = uid
        self.shortcut_overrode_keyevent = False
        self._changed = False
        self.wait_for_autocomplete = False
        self._handle_shortcuts = handle_shortcuts
        self._features_initialised = False
        self._key_pressed = False
        self.last_key_pressed = ''

        self.emit_text_changed = True
        self.textChanged.connect(
            self._handle_textChanged
        )

        linenumberarea.LineNumberArea(self)

        if init_features:
            self.init_features()

    def init_features(self):
        """
        Initialise custom Editor features.
        """
        if self._features_initialised:
            return
        self._features_initialised = True

        # QSyntaxHighlighter causes
        # textChanged to be emitted,
        # which we don't want.
        self.emit_text_changed = False
        syntaxhighlighter.Highlight(
            self.document(),
            self
        )
        def set_text_changed_enabled():
            self.emit_text_changed = True
        QtCore.QTimer.singleShot(
            0,
            set_text_changed_enabled
        )

        CM = contextmenu.ContextMenu
        self.contextmenu = CM(self)

        # TODO: add a new autocompleter
        # that uses DirectConnection.
        self.wait_for_autocomplete = True
        AC = autocompletion.AutoCompleter
        self.autocomplete = AC(self)

        if self._handle_shortcuts:
            actions.Actions(
                editor=self,
            )
            shortcuts.ShortcutHandler(
                editor=self,
                use_tabs=False
            )

    def _handle_textChanged(self):
        self._changed = True

        # emit custom textChanged when desired.
        if self.emit_text_changed:
            self.text_changed_signal.emit()

    def setTextChanged(self, state=True):
        self._changed = state

    def replace_text(self, text):
        """
        Set the text programmatically
        but allow an undo. Works around
        setPlainText automatically
        resetting the undo stack.
        """
        tc = self.textCursor()
        tc.beginEditBlock()
        tc.select(tc.Document)
        tc.removeSelectedText()
        self.appendPlainText(text)
        tc.endEditBlock()

    def setPlainText(self, text):
        """
        Override original method to prevent
        textChanged signal being emitted.
        WARNING: textCursor can still be used
        to setPlainText.
        """
        self.emit_text_changed = False
        super(Editor, self).setPlainText(text)
        self.emit_text_changed = True

    def insertPlainText(self, text):
        """
        Override original method to prevent
        textChanged signal being emitted.
        """
        self.emit_text_changed = False
        super(Editor, self).insertPlainText(text)
        self.emit_text_changed = True

    def appendPlainText(self, text):
        """
        Override original method to prevent
        textChanged signal being emitted.
        """
        self.emit_text_changed = False
        super(Editor, self).appendPlainText(text)
        self.emit_text_changed = True

    def focusInEvent(self, event):
        """
        Emit a signal when focusing in a window.
        When there used to be an editor per tab,
        this would work well to check that the tab's
        contents had not been changed. Now, we'll
        also want to signal from the tab switched
        signal.
        """
        FR = QtCore.Qt.FocusReason
        ignored_reasons = [
            FR.PopupFocusReason,
        ]
        if event.reason() not in ignored_reasons:
            self.focus_in_signal.emit(event)
        super(Editor, self).focusInEvent(event)

    def focusOutEvent(self, event):
        if self._changed:
            self.editingFinished.emit()
        self.text_changed_signal.emit()

        FR = QtCore.Qt.FocusReason
        ignored_reasons = [
            FR.PopupFocusReason,
        ]
        if event.reason() not in ignored_reasons:
            self.focus_out_signal.emit(event)

        super(Editor, self).focusOutEvent(event)

    def resizeEvent(self, event):
        """
        Emit signal on resize so that the
        LineNumberArea has a chance to update.
        """
        super(Editor, self).resizeEvent(event)
        self.resize_signal.emit(event)

    def keyPressEvent(self, event):
        """
        Emit signals for key events
        that QShortcut cannot override.
        """
        self._key_pressed = True

        if not self.hasFocus():
            event.ignore()
            return

        if self.wait_for_autocomplete:
            self.key_pressed_signal.emit(event)
            return

        self.shortcut_overrode_keyevent = False
        self.shortcut_signal.emit(event)
        if self.shortcut_overrode_keyevent:
            event.accept()
            return

        super(Editor, self).keyPressEvent(event)
        self.post_key_pressed_signal.emit(event)

    def keyReleaseEvent(self, event):
        self._key_pressed = False
        if not isinstance(self, Editor):
            # when the key released is F5
            # (reload app)
            return
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

    def event(self, event):
        """
        Drop to open files implemented as a filter
        instead of dragEnterEvent and dropEvent
        because it is the only way to make it work
        on windows.
        """
        if event.type() == event.DragEnter:
            mimeData = event.mimeData()
            if mimeData.hasUrls():
                event.accept()
                return True
        if event.type() == event.Drop:
            mimeData = event.mimeData()
            if mimeData.hasUrls():
                event.accept()
                urls = mimeData.urls()
                self.drop_files(urls)
                return True
        try:
            return super(Editor, self).event(event)
        except TypeError:
            return False

    def drop_files(self, urls):
        """
        When dragging and dropping files onto the
        editor from a source with urls (file paths),
        if there are tabs, open the files in new
        tabs. If the tabs are not present just insert
        the text into the editor.
        """
        if self._handle_shortcuts:
            # if we're handling shortcuts
            # it means there are no tabs.
            # just insert the text
            text_list = []
            for url in urls:
                path = url.toLocalFile()
                with open(path, 'r') as f:
                    text_list.append(f.read())

            self.textCursor(
                ).insertText(
                '\n'.join(text_list)
            )
        else:
            tabeditor = self.parent()
            for url in urls:
                path = url.toLocalFile()
                actions.open_action(
                    tabeditor.tabs,
                    self,
                    path
                )

    def wheelEvent(self, event):
        """
        Restore focus and, if ctrl held, emit signal
        """
        self.setFocus(QtCore.Qt.MouseFocusReason)
        vertical = QtCore.Qt.Orientation.Vertical
        is_vertical = (
            event.orientation() == vertical
        )
        CTRL = QtCore.Qt.ControlModifier
        is_ctrl = (event.modifiers() == CTRL)
        if is_ctrl and is_vertical:
            return self.wheel_signal.emit(event)
        super(Editor, self).wheelEvent(event)

    def insertFromMimeData(self, mimeData):
        """
        Override to emit text_changed_signal
        (which triggers autosave) when text
        is pasted or dragged in.
        """
        self.text_changed_signal.emit()
        super(
            Editor, self
            ).insertFromMimeData(mimeData)

    def showEvent(self, event):
        self.setFocus(QtCore.Qt.MouseFocusReason)
        super(Editor, self).showEvent(event)
