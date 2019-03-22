# THIS is the implementation I should use
from Qt import QtWidgets, QtGui, QtCore, QtTest
#import nukescripts
import json
import time
from PythonEditor.ui.features import actions
reload(actions)


def get_action_dict():

    json_path = 'C:/Repositories/PythonEditor/PythonEditor/ui/features/action_register.json'

    with open(json_path, 'r') as f:
        action_dict = json.load(f)

    #print json.dumps(action_dict, indent=2)
    return action_dict


def get_shortcuts():
    action_dict = get_action_dict()
    shortcuts = []
    for widget_name, widget_actions in action_dict.items():
        for name, attributes in widget_actions.items():
            strokes = attributes['Shortcuts']
            for shortcut in strokes:
                shortcuts.append(str(shortcut))
    return shortcuts

def get_actions(widget_name):
    action_dict = get_action_dict()
    actions = {}
    widget_actions = action_dict[widget_name]
    for name, attributes in widget_actions.items():
        strokes = attributes['Shortcuts']
        method = attributes['Method']
        for shortcut in strokes:
            actions[shortcut] = method
    return actions


def key_to_shortcut(key):
    """
    Convert the given QtCore.Qt.Key type
    to a string including currently held modifiers.
    """
    modifier_map = {
        QtCore.Qt.Key_Control: QtCore.Qt.ControlModifier,
        QtCore.Qt.Key_Shift: QtCore.Qt.ShiftModifier,
        QtCore.Qt.Key_Alt: QtCore.Qt.AltModifier,
        QtCore.Qt.Key_Meta: QtCore.Qt.MetaModifier,
    }
    held = QtWidgets.QApplication.keyboardModifiers()
    #held_keys = tuple(
        #mod for mod in modifier_map.values()
        #if held & mod == mod
    #)
    #combo = 0
    #for mod in held_keys:
        #combo |= mod
    #combo |= key

    combo = 0
    for mod in modifier_map.values():
        if held & mod == mod:
            combo |= mod
    combo |= key

    combo = QtGui.QKeySequence(combo).toString()
    try:
        combo = str(combo)
    except UnicodeEncodeError:
        combo = repr(combo)
    return combo





class KeyCatcher(QtWidgets.QPlainTextEdit):
    shortcut_signal = QtCore.Signal(unicode)
    def __init__(self):
        super(KeyCatcher, self).__init__()
        self.wait_for_autocomplete = False

    def keyPressEvent(self, event):
        shortcut = key_to_shortcut(event.key())
        self.shortcut_handled = False
        self.shortcut_signal.emit(shortcut)
        if self.shortcut_handled:
            return
        super(KeyCatcher, self).keyPressEvent(event)


class Shortcuts(QtCore.QObject):
    def __init__(self, editor):
        super(Shortcuts, self).__init__()
        self.setParent(editor)
        self.editor = editor
        self.action_manager = editor.action_manager
        editor.shortcut_signal.connect(
            self.dispatch,
            QtCore.Qt.DirectConnection
        )
        self.lookup = get_actions('editor')

    def dispatch(self, shortcut):
        name = self.lookup.get(shortcut)
        if name is None:
            return
        method = getattr(self.action_manager, name)
        if method is None:
            return
        method.__call__()
        self.editor.shortcut_handled = True


#&& # test 1
k = KeyCatcher()
ACTIONS = actions.Actions(editor=k)
k.action_manager = ACTIONS
k.shortcuts = Shortcuts(k)
k.show()


#&& # test 2
for key in QtCore.Qt.Key.values.values():
    print key_to_shortcut(key)
#&&
