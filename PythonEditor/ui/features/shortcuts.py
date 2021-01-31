from __future__ import print_function
import __main__
import logging
from functools import partial

from PythonEditor.ui.Qt.QtWidgets import (
    QAction, QApplication)
from PythonEditor.ui.Qt.QtGui import (
    QKeyEvent, QKeySequence)
from PythonEditor.ui.Qt.QtCore import (
    Slot, QEvent, QCoreApplication, Qt, QObject)

from PythonEditor.ui.features import actions
from PythonEditor.utils.signals import connect
from PythonEditor.utils.log import logger as lgr


def debug(message):
    print(message)
    import nuke
    nuke.tprint(message)

def load_actions():
    return actions.load_actions_from_json()


def key_to_sequence(key):
    """Convert the given Qt.Key type to a
    QKeySequence including currently held
    modifiers. The only downside to this being
    that, for keys that require shift to be held,
    the sequence Shift+Key will be returned.
    """
    modifier_map = {
        Qt.Key_Control : Qt.ControlModifier,
        Qt.Key_Shift   : Qt.ShiftModifier,
        Qt.Key_Alt     : Qt.AltModifier,
        Qt.Key_Meta    : Qt.MetaModifier,
    }
    app = QApplication
    held = app.keyboardModifiers()
    combo = 0
    for mod in modifier_map.values():
        if held & mod == mod:
            combo |= mod
    combo |= key

    combo = QKeySequence(combo)
    return combo


class ShortcutHandler(QObject):
    """Shortcut Manager with custom signals.

    :param editor: required `QPlainTextEdit` or `Editor` class.
    :param tabeditor: optional `QWidget` or `TabEditor`
    :param terminal: optional `QPlainTextEdit` or `Terminal` class.
    """
    def __init__(
            self,
            editor=None,
            tabeditor=None,
            terminal=None,
        ):
        super(ShortcutHandler, self).__init__()
        self.setObjectName('ShortcutHandler')
        self._installed = False

        if editor is None:
            raise Exception("""
            A text editor is necessary
            for this class.
            """.strip()
            )
        self.editor = editor

        if tabeditor is not None:
            self.tabeditor = tabeditor
            self.tabs = tabeditor.tabs
            parent_widget = tabeditor
        else:
            parent_widget = editor

        if terminal is not None:
            self.terminal = terminal
        self.parent_widget = parent_widget
        self.setParent(parent_widget)

        self.shortcut_dict = {}
        self.unassigned = []

        self.register_all_shortcuts()
        self.editor.installEventFilter(self)


    def eventFilter(self, obj, event):
        """This was such a complicated override for a while.
        It used to be on the whole application, but now it lives
        only on the editor, and accepts shortcut events to trigger
        registered actions. A bit of of keypress handling is performed
        for more complex scenarios such as Tab and [ keys."""
        try:
            QEvent.Shortcut
            QEvent.ShortcutOverride
            QEvent.KeyPress
        except AttributeError:
            # the following events cause an error, because "QEvent" is "None" while the module is reloading.
            # potential solution: use event.Shortcut, event.ShortcutOverride, event.KeyPress ?
            # event.Hide
            # event.FocusAboutToChange
            # event.FocusOut
            # event.Destroy
            return False

        if event.type() in [event.Shortcut, event.ShortcutOverride]: # accept all shortcuts
            event.accept()
            return True

        if event.type() == event.KeyPress:
            # only let the editor receive keypress overrides
            if obj == self.editor:
                return self.handle_keypress(event)

        return False

    @Slot(QKeyEvent)
    def handle_keypress(self, event):

        held = QApplication.keyboardModifiers()

        if (event.isAutoRepeat()
            and held == Qt.NoModifier
            ):
            return False

        key = event.key()
        if key in [
           Qt.Key_Control,
           Qt.Key_Shift,
           Qt.Key_Alt,
           Qt.Key_AltGr,
           Qt.Key_Meta,
        ]:
            return False

        # is it a Tab after a dot?
        if key == Qt.Key_Tab:
            cursor = self.editor.textCursor()
            cursor.select(cursor.LineUnderCursor)
            text = cursor.selectedText()
            if text.endswith('.'):
                # allow autocompletion to handle this
                return False

        # try with event.text() for things
        # like " and { which appear as
        # shift+2 and shift+[ respectively
        action = self.shortcut_dict.get(
            event.text()
        )

        single_key = (action is not None)
        if not single_key:
            combo = key_to_sequence(key)
            shortcut = combo.toString()
            action = self.shortcut_dict.get(
                shortcut
            )

        if action is None:
            return False

        # need some way for the key to be
        # recognised, for example in wrap_text
        e = self.editor
        e.last_key_pressed = event.text()
        action.trigger()
        e.shortcut_overrode_keyevent = True
        if single_key:
            # it's a single key. let the
            # autocomplete do its thing
            e.post_key_pressed_signal.emit(event)
        return True

    def register_all_shortcuts(self):
        """
        Load a set of shortcuts per actions per widget.
        The register `dict` is loaded from the 
        action_register.json along with any user overrides.
        (See load_actions_from_json documentation.)

        "tabs": {                        # widget name
            "New Tab": {                 # action name
                "Shortcuts": [           # list of shortcuts
                    "Ctrl+T",            # shortcut string to be translated
                    "Ctrl+Shift+N",
                    "Ctrl+N"
                ],
                "Menu Location": "File", # menu location
                "Method": "new_tab"      # method name on the Actions class.
            },
        "terminal": {
            "Clear Output Signal": {
                "Shortcuts": [
                    "Ctrl+Backspace"
                ],
                "Method": "clear_output",
                "Menu Location": "View"
            },

        """
        register = load_actions()
        for wname, actions in register.items():
            self.register_widget_shortcuts(wname, actions)

    def register_widget_shortcuts(self, wname, actions):
        """
        Check if the widget has been stored on this class
        as an attribute, and if so, proceed to apply shortcuts
        to that widget.

        :param wname: `str` name of the widget. One of:
        editor, tabeditor, terminal.
        :param actions: `dict` of `str`:`dict` pairs
        """

        # widget name was set in this class's __init__()
        widget = getattr(self, wname, None)
        if widget is None:
            return

        for action_name, attributes in actions.items():
            self.add_shortcuts(widget, action_name, attributes)

    def add_shortcuts(self, widget, aname, attrs):
        """
        Set shortcuts to their related actions on the given widget.

        :param widget: subclass of `QWidget` the shortcut belongs to.
        :param aname: `str` name of the `QAction`
        :param attrs: `dict` of `str`:`str` containing shortcuts.
        """
        action = self.get_action_by_name(widget, aname)
        if action is None:
            return

        shortcuts = attrs['Shortcuts']
        if len(shortcuts) == 0:
            self.unassigned.append(action)
            return
            
        key_seqs = []
        for shortcut in shortcuts:
            key_seq = QKeySequence(
                shortcut
            )

            # convert to unicode again
            # to make sure the format
            # stays the same
            s = key_seq.toString()
            self.shortcut_dict[s] = action
            key_seqs.append(key_seq)

        action.setShortcuts(key_seqs)
        action.setShortcutContext(
            Qt.WidgetWithChildrenShortcut
        )

    def get_action_by_name(self, widget, aname):
        """
        Lookup an action of a widget by name.

        :param widget: subclass of `QWidget` the action belongs to.
        :param aname: `str` name of the QAction
        """
        for action in widget.actions():
            if action.text() == aname:
                return action




# TODO: perhaps eventFilter is a little brute force? it intercepts EVERY event in the program.
# however, would event() need to be implemented on each widget class? TabEditor, Editor, Terminal?
# or could each class just implement it and let the same ShortcutHandler handle it?

"""
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from PythonEditor.ui.editor import Editor
from PythonEditor.ui.features.shortcuts import load_actions


SHORTCUTS = {}
register = load_actions()
for wname, actions in register.items():
    for action_name, attributes in actions.items():
        shortcuts = attributes['Shortcuts']
        for shortcut in shortcuts:
            SHORTCUTS[shortcut] = action_name

class Text(Editor):
    def event(self, event):
        # Can intercept everything!
        # event.accept()
        if event.type() in [QEvent.KeyPress, QEvent.KeyRelease]:
            shortcut = QKeySequence(event.modifiers()|event.key()).toString()
            if SHORTCUTS.get(shortcut):
                event.accept()
                if event.isAutoRepeat():
                    return False
                print shortcut, SHORTCUTS.get(shortcut)
                return True

            key = event.key()
            print 'key', key # do key stuff
            if key == 32:
                if event.modifiers() == Qt.ControlModifier:
                    return True
        elif event.type() in [QEvent.Shortcut, QEvent.ShortcutOverride, 32]:
            print 'shortcut!' # do shortcut stuff
            return True
        elif event.type() in [QEvent.UpdateRequest]:
            return super(Text, self).event(event)
        else:
            # bye! let parent handle this one
            print 'type:', event.type()
            try:
                return super(Text, self).event(event)
            except TypeError:
                return False
        
        # print event.type()
        super(Text, self).event(event)
        return True # we want ALL shortcuts, thanks



import nukescripts
panel = nukescripts.registerWidgetAsPanel('Text', 'test text', 'test.text.id', create=True)
panel.addToPane(nuke.thisPane())

"""
