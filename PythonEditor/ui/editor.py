"""
This module contains the main text editor that can be
run independently, embedded in other layouts, or used
within the tabbed editor to have different contents
per tab.
"""

import os
import uuid
import __main__
from PythonEditor.ui.Qt.QtWidgets import (
    QPlainTextEdit, QMenu)
from PythonEditor.ui.Qt.QtGui import (
    QFocusEvent, QFocusEvent, QWheelEvent,
    QKeyEvent, QResizeEvent, QFont)
from PythonEditor.ui.Qt.QtCore import (
    Signal, Slot, QTimer, Qt, QMimeData, QByteArray)

from PythonEditor import six
from PythonEditor.utils import constants
from PythonEditor.ui.features import actions
from PythonEditor.ui.features import shortcuts
from PythonEditor.ui.features import linenumberarea
from PythonEditor.ui.features import syntaxhighlighter
from PythonEditor.ui.features import autocompletion
from PythonEditor.ui.features import contextmenu


def sanitize_text(text):
    if isinstance(text, QByteArray):
        text = text.data()
    if isinstance(text, bytes):
        # tabs cause Nuke to crash
        if b'\t' in text:
            text = text.replace(b'\t', b'    ')
    elif isinstance(text, six.string_types):
        if '\t' in text:
            text = text.replace('\t', '    ')
    return text


def sanitize_mimedata(mimedata):
    new_mimedata = QMimeData()
    for fmt in mimedata.formats():
        data = mimedata.data(fmt)

        data = sanitize_text(data)
        new_mimedata.setData(fmt, data)
    return new_mimedata


class Editor(QPlainTextEdit):
    """Code Editor widget. Extends QPlainTextEdit to
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

    wrap_signal               = Signal(str)
    uuid_signal               = Signal(str)
    return_signal             = Signal(QKeyEvent)
    focus_in_signal           = Signal()
    focus_out_signal          = Signal()
    post_key_pressed_signal   = Signal(QKeyEvent)
    wheel_signal              = Signal(QWheelEvent)
    key_pressed_signal        = Signal(QKeyEvent)
    shortcut_signal           = Signal(QKeyEvent)
    resize_signal             = Signal(QResizeEvent)
    context_menu_signal       = Signal(QMenu)
    tab_signal                = Signal()
    home_key_signal           = Signal()
    relay_clear_output_signal = Signal()
    editingFinished           = Signal()
    text_changed_signal       = Signal()
    selection_stopped         = Signal()

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
        font = QFont(DEFAULT_FONT)
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
            uid = str(uuid.uuid1())
        self.shortcut_overrode_keyevent = False
        self._changed = False
        self.autocomplete_overriding = False
        self._handle_shortcuts = handle_shortcuts
        self._features_initialised = False
        self._key_pressed = False
        self.last_key_pressed = ''

        self.emit_text_changed = True
        self.textChanged.connect(
            self._handle_textChanged)

        self._selection_timer = QTimer()
        self._selection_timer.setInterval(1000)
        self._selection_timer.setSingleShot(True)
        self._selection_timer.timeout.connect(
            self.selection_stopped.emit)
        self.selectionChanged.connect(
            self._handle_selectionChanged)

        linenumberarea.LineNumberArea(self)

        if init_features:
            self.init_features()

    def init_features(self):
        """Initialise custom Editor features.
        """
        if self._features_initialised:
            return
        self._features_initialised = True

        # QSyntaxHighlighter causes
        # textChanged to be emitted,
        # which we don't want.
        self.emit_text_changed = False
        syntaxhighlighter.Highlight(self.document(), self)
        def set_text_changed_enabled():
            self.emit_text_changed = True
        QTimer.singleShot(0, set_text_changed_enabled)

        CM = contextmenu.ContextMenu
        self.contextmenu = CM(self)

        # TODO: add a new autocompleter
        # that uses an eventfilter.
        self.autocomplete_overriding = True
        AC = autocompletion.AutoCompleter
        self.autocomplete = AC(self)

        if self._handle_shortcuts:
            actions.Actions(editor=self)
            shortcuts.ShortcutHandler(editor=self)

    @Slot()
    def _handle_textChanged(self):
        self._changed = True

        # emit custom textChanged when desired.
        if self.emit_text_changed:
            self.text_changed_signal.emit()

    @Slot()
    def _handle_selectionChanged(self):
        """Emit a selection_stopped signal once
        the selection has stopped changing after a
        certain time interval defined on the
        _selection_timer.
        """
        if not self._selection_timer.isActive():
            self._selection_timer.start()

    def setTextChanged(self, state=True):
        self._changed = state

    def selected_text(self):
        return self.textCursor().selection().toPlainText()

    def replace_text(self, text):
        """Set the text programmatically
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
        """Override original method to prevent
        textChanged signal being emitted.
        WARNING: textCursor can still be used
        to setPlainText.
        """
        self.emit_text_changed = False
        super(Editor, self).setPlainText(text)
        self.emit_text_changed = True

    def insertPlainText(self, text):
        """Override original method to prevent
        textChanged signal being emitted.
        """
        self.emit_text_changed = False
        super(Editor, self).insertPlainText(text)
        self.emit_text_changed = True

    def appendPlainText(self, text):
        """Override original method to prevent
        textChanged signal being emitted.
        """
        self.emit_text_changed = False
        super(Editor, self).appendPlainText(text)
        self.emit_text_changed = True

    def focusInEvent(self, event):
        """Emit a signal when focusing in a window.
        When there used to be an editor per tab,
        this would work well to check that the tab's
        contents had not been changed. Now, we'll
        also want to signal from the tab switched
        signal.
        """
        # ignore PopupFocusReason as the
        # autocomplete QListView triggers it.
        ignored_reasons = [
            Qt.PopupFocusReason,
        ]
        if event.reason() not in ignored_reasons:
            # FIXME:
            # AttributeError: 'PySide2.QtCore.QEvent' object has no attribute 'reason'
            self.focus_in_signal.emit()
        super(Editor, self).focusInEvent(event)

    def focusOutEvent(self, event):
        if not isinstance(event, QFocusEvent):
            if os.getenv('USER') == 'mlast':
                # why would a focus out handler
                # be receiving an event of the
                # wrong type?
                print(dir(event), event.type())
                # AttributeError: 'PySide2.QtCore.QEvent' object has no attribute 'sender'
            return

        if self._changed:
            self.editingFinished.emit()

        # emit text changed to store the
        # latest text within the tab
        # FIXME: I don't like that this is here. at the very least it should be a more generic request_autosave signal.
        self.text_changed_signal.emit()

        ignored_reasons = [
            Qt.PopupFocusReason,
        ]
        if event.reason() not in ignored_reasons:
            self.focus_out_signal.emit()

        super(Editor, self).focusOutEvent(event)

    def resizeEvent(self, event):
        """Emit signal on resize so that the
        LineNumberArea has a chance to update.
        """
        super(Editor, self).resizeEvent(event)
        self.resize_signal.emit(event)

    def keyPressEvent(self, event):
        """Emit signals for key events
        that QShortcut cannot override.
        """
        self._key_pressed = True

        if not self.hasFocus():
            event.ignore()
            return

        # print('Editor: {!r} has been pressed.'.format(event.text()))
        if self.autocomplete_overriding:
            # let the autocomplete handle the
            # key press (i.e. complete the text)
            self.key_pressed_signal.emit(event)
            return

        self.shortcut_overrode_keyevent = False
        self.shortcut_signal.emit(event)
        if self.shortcut_overrode_keyevent:
            event.accept()
            return

        # print('Editor: {!r} will be entered.'.format(event.text()))
        super(Editor, self).keyPressEvent(event)
        self.post_key_pressed_signal.emit(event)

    def keyReleaseEvent(self, event):
        self._key_pressed = False
        if not isinstance(self, Editor):
            # when the key released is F5
            # (reload app)
            return
        self.autocomplete_overriding = True
        super(Editor, self).keyReleaseEvent(event)

    def contextMenuEvent(self, event):
        """Creates a standard context menu
        and emits it for futher changes
        and execution elsewhere.
        """
        menu = self.createStandardContextMenu()
        self.context_menu_signal.emit(menu)

    def event(self, event):
        """Drop to open files implemented as a filter
        instead of dragEnterEvent and dropEvent
        because it is the only way to make it work
        on windows.
        """
        if event.type() == event.DragEnter:
            mimeData = event.mimeData()
            if mimeData.hasUrls():
                event.accept()
                return True
        elif event.type() == event.Drop:
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
        """When dragging and dropping files onto the
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
        """Restore focus and, if ctrl held, emit signal
        """
        self.setFocus(Qt.MouseFocusReason)
        vertical = Qt.Orientation.Vertical
        is_vertical = (
            event.orientation() == vertical
        )
        CTRL = Qt.ControlModifier
        ctrl_held = (event.modifiers() == CTRL)
        if ctrl_held and is_vertical:
            return self.wheel_signal.emit(event)
        super(Editor, self).wheelEvent(event)

    def insertFromMimeData(self, mimedata):
        """Override to emit text_changed_signal
        (which triggers autosave) when text
        is pasted or dragged in.
        """
        self.text_changed_signal.emit()
        mimedata = sanitize_mimedata(mimedata)
        super(Editor, self).insertFromMimeData(mimedata)

    def showEvent(self, event):
        """Override to automatically set the
        focus on the editor when shown.
        """
        super(Editor, self).showEvent(event)

        # Previously, this used PopupFocusReason,
        # which doesn't trigger the autosave via
        # the focus_in_signal.
        self.setFocus(Qt.ShortcutFocusReason)
