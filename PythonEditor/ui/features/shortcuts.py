from __future__ import print_function
import __main__
from functools import partial

from PythonEditor.ui.Qt import QtWidgets, QtGui, QtCore
from PythonEditor.utils.signals import connect
from PythonEditor.ui.features import actions

# FIXME:
# Shift+Home doesn't select
# wrap_handler doesn't know which key was pressed (store it on the editor?)
class ShortcutHandler(QtCore.QObject):
    """
    Shortcut Manager with custom signals.
    """
    clear_output_signal = QtCore.Signal()
    exec_text_signal = QtCore.Signal()

    def __init__(
            self,
            editor=None,
            tabeditor=None,
            terminal=None,
            use_tabs=True
        ):
        """
        :param editor:
        :param tabeditor:
        :param terminal:
        :param use_tabs:
        """
        super(ShortcutHandler, self).__init__()
        self.setObjectName('ShortcutHandler')
        self.use_tabs = use_tabs

        if editor is None:
            raise Exception(
                'A text editor is necessary for this class.'
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
            self.clear_output_signal.connect(
                self.terminal.clear
            )
        self.parent_widget = parent_widget

        self.setParent(parent_widget)
        self.all_shortcuts = []

        self.register_shortcuts()
        self.connect_signals()

    def connect_signals(self):
        """
        Connects the current editor's
        signals to this class
        """
        self.editor.shortcut_signal.connect(
            self.handle_keypress,
            QtCore.Qt.DirectConnection
        )

    QtCore.Slot(QtGui.QKeyEvent)
    def handle_keypress(self, event):
        
        # if event.isAutoRepeat():
        #     return

        key = event.key()
        if key in [
            QtCore.Qt.Key_Control,
            QtCore.Qt.Key_Shift,
            QtCore.Qt.Key_Alt,
            QtCore.Qt.Key_AltGr,
            QtCore.Qt.Key_Meta,
        ]:
            return

        stroke = key
        modifiers = event.modifiers()
        stroke = modifiers | key
        # TODO: need some way for the key
        # to be recognised, for example in wrap_text
        if not self.find_stroke(stroke):
            if not self.find_stroke(key):
                return
        self.editor.shortcut_overrode_keyevent = True

    def find_stroke(self, stroke):
        key_seq = QtGui.QKeySequence(stroke)
        text = key_seq.toString()
        for ks, action in self.all_shortcuts:
            if ks == key_seq:
                # print(ks, action, text)
                action.trigger()
                return True
        return False

    def register_shortcuts(self, action_dict=None):
        """
        Use the shortcut register to apply shortcuts
        to actions that exist on the widget.
        """
        if action_dict is None:
            action_dict = actions.load_actions_from_json()

        for widget_name, widget_actions in action_dict.items():
            if not hasattr(self, widget_name):
                continue
            widget = getattr(self, widget_name)
            if widget is None:
                continue
            for action_name, attributes in widget_actions.items():
                shortcuts = attributes['Shortcuts']
                if len(shortcuts) == 0:
                    continue
                for action in widget.actions():
                    if action.text() != action_name:
                        continue
                    break
                else:
                    continue
                key_seqs = []
                for shortcut in shortcuts:
                    key_seq = QtGui.QKeySequence(shortcut)
                    self.all_shortcuts.append(
                        (key_seq, action)
                        )
                    key_seqs.append(key_seq)

                action.setShortcuts(key_seqs)
                action.setShortcutContext(
                    QtCore.Qt.WidgetShortcut
                )
