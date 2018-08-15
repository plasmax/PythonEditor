"""
Rationale: allow users to override the config
using custom json files that list function names
paired with key sequences.
"""
import imp
import json
import os
import shortcut_functions

__folder__ = os.path.dirname(__file__)
__project__ = os.path.dirname(__folder__)
# TEMP! This will be your .nuke dir
__configs__ = __folder__
shortcut_config_path = os.path.join(__configs__, 'shortcut_config.json')


qt_path = os.path.join(__project__, 'PythonEditor/ui/Qt.py')
Qt = imp.load_source('Qt', qt_path)
QtWidgets, QtGui, QtCore = Qt.QtWidgets, Qt.QtGui, Qt.QtCore

# BUG: json loads as unicode, this causes problems.
# with open(shortcut_config_path, 'rt') as f:
#     SHORTCUT_CONFIG = json.loads(f.read())


SHORTCUT_CONFIG = {
    "signal_dict": {
        "return_handler": "Return/Enter",
        "wheel_zoom": "Ctrl+Mouse Wheel",
        "move_to_bottom": "Ctrl+Alt+End",
        "jump_to_start": "Home",
        "clear_output_signal": "Ctrl+Backspace",
        "wrap_text": [
            "'",
            "\"",
            "(",
            ")",
            "[",
            "]",
            "\\{",
            "\\}"
        ],
        "cut_line": "Ctrl+X",
        "move_to_top": "Ctrl+Alt+Home",
        "tab_handler": "Tab"
    },
    "tab_shortcuts": {
        "editortabs.new_tab": "Ctrl+Shift+N",
        "editortabs.close_current_tab": "Ctrl+Shift+W"
    },
    "editor_shortcuts": {
        "previous_tab": "Ctrl+Shift+Tab",
        "new_line_above": "Ctrl+Shift+Return",
        "delete_to_start_of_line": "Ctrl+Shift+Backspace",
        "hop_brackets": "Ctrl+M",
        "zoom_in": [
            "Ctrl+=",
            "Ctrl++"
        ],
        "duplicate_lines": "Ctrl+Shift+D",
        "search_input": "Ctrl+Shift+F",
        "new_line_below": "Ctrl+Alt+Return",
        "delete_lines": "Ctrl+Shift+K",
        "print_help": "Ctrl+H",
        "return_handler": [
            "Return",
            "Enter"
        ],
        "zoom_out": "Ctrl+-",
        "move_lines_up": "Ctrl+Shift+Up",
        "select_word": "Ctrl+D",
        "print_type": "Ctrl+T",
        "comment_toggle": "Ctrl+/",
        "wrap_text": [
            "'",
            "\"",
            "(",
            ")",
            "[",
            "]",
            "Shift+{",
            "Shift+}"
        ],
        "delete_to_end_of_line": "Ctrl+Shift+Delete",
        "unindent": [
            "Ctrl+[",
            "Shift+Tab"
        ],
        "indent": "Ctrl+]",
        "select_between_brackets": "Ctrl+Shift+M",
        "next_tab": "Ctrl+Tab",
        "exec_current_line": "Ctrl+B",
        "move_lines_down": "Ctrl+Shift+Down",
        "join_lines": "Ctrl+J",
        "select_lines": "Ctrl+L"
    }
}
# print SHORTCUT_CONFIG
# with open(shortcut_config_path, 'rt') as f:



# cfg = json.dumps(SHORTCUT_CONFIG, indent=4)
# with open(shortcut_config_path, 'wt') as f:
#     f.write(cfg)

event_types = (QtCore.QEvent.KeyPress,
               QtCore.QEvent.KeyRelease,
               QtCore.QEvent.ShortcutOverride)

mods = {
    QtCore.Qt.Key_Control: QtCore.Qt.ControlModifier,
    QtCore.Qt.Key_Shift: QtCore.Qt.ShiftModifier,
    QtCore.Qt.Key_Alt: QtCore.Qt.AltModifier,
}


def ints(arg):
    try:
        return int(arg)
    except Exception:
        return None


def map_shortcut_to_function(shortcut, function, widget):
    context = QtCore.Qt.WidgetShortcut
    key_sequence = QtGui.QKeySequence(shortcut)
    qshortcut = QtWidgets.QShortcut(key_sequence,
                                    widget,
                                    function,
                                    context=context)
    qshortcut.setObjectName(shortcut)


def get_register(widget, category):
    register = []
    for function_name, shortcut in SHORTCUT_CONFIG[category].items():
        function = getattr(shortcut_functions, function_name)
        # function = partial(function, widget)
        if isinstance(shortcut, str):
            shortcut = QtGui.QKeySequence(shortcut)
            register.append((shortcut, function))
        else:
            for sub in shortcut:
                shortcut = QtGui.QKeySequence(sub)
                shortcut = sub
                register.append((shortcut, function))
    return register


def apply_shortcut_register(widget, category='editor_shortcuts'):
    register = get_register(widget, category)
    for shortcut, function in register:
        map_shortcut_to_function(shortcut, function, widget)


class Shortcuts(QtCore.QObject):
    def __init__(self, widget, register):
        super(Shortcuts, self).__init__()
        self.widget = widget
        self.register = register

        self.keylist = []
        self.keyseq = QtGui.QKeySequence()
        self.qtkeys = [getattr(QtCore.Qt.Key, key)
                       for key in dir(QtCore.Qt.Key)]
        self.keys = {ints(key): key
                     for key in self.qtkeys}

        self.widget.installEventFilter(self)

    def eventFilter(self, obj, event):
        if not self.widget.hasFocus():
            return False

        if event.type() == QtCore.QEvent.KeyPress:
            self.key_press(event)

            s = 0
            for i in self.keylist:
                s |= i
            seq = QtGui.QKeySequence(s)
            for keyseq, func in self.register:
                if keyseq == seq:
                    event.accept()
                    print func
                    try:
                        func(self.widget)
                    except TypeError:
                        func(self.widget, event.text())
                    return True
            return False

        if event.type() == QtCore.QEvent.KeyRelease:
            self.keyseq = QtGui.QKeySequence()
            self.key_release(event)

        return False

    def key_press(self, event):
        astr = self.keys[event.key()]
        astr = mods.get(astr, astr)
        self.keylist.append(astr)

    def key_release(self, event):
        del self.keylist[-1]


def main():

    app = QtWidgets.QApplication([])
    widget = QtWidgets.QPlainTextEdit()
    register = get_register(widget, 'editor_shortcuts')
    shortcut_filter = Shortcuts(widget, register)
    Shortcuts(widget, register)
    # apply_shortcut_register(widget)
    widget.show()

    app.exec_()


if __name__ == '__main__':
    main()




# QtGui.QKeySequence(shortcut)
