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


def json_load_byteified(file_handle):
    return _byteify(
        json.load(file_handle, object_hook=_byteify),
        ignore_dicts=True
    )


def json_loads_byteified(json_text):
    return _byteify(
        json.loads(json_text, object_hook=_byteify),
        ignore_dicts=True
    )


def _byteify(data, ignore_dicts=False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [_byteify(item, ignore_dicts=True) for item in data]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data


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

config_dict = {}
for key in SHORTCUT_CONFIG.keys():
    config_dict[key] = {}
    for k, v in SHORTCUT_CONFIG[key].items():
        if isinstance(v, list):
            for i in v:
                config_dict[key][i] = k
        else:
            config_dict[key][v] = k

# print json.dumps(config_dict, indent=4)

config_dict = {
    'signal_dict': {
        'Ctrl+Mouse Wheel':                  'wheel_zoom',
    },
    'tab_shortcuts': {
        'Ctrl+Shift+N':              'editortabs.new_tab',
        'Ctrl+Shift+W':    'editortabs.close_current_tab',
    },
    'editor_shortcuts': {
        # 'Ctrl+Backspace':           'clear_output_signal',
        'Ctrl+Alt+Home':                    'move_to_top',
        'Ctrl+Alt+End':                  'move_to_bottom',
        'Tab':                              'tab_handler',
        'Home':                           'jump_to_start',
        'Ctrl+X':                              'cut_line',
        'Ctrl+B':                     'exec_current_line',
        'Ctrl+D':                           'select_word',
        'Ctrl+H':                            'print_help',
        'Ctrl+J':                            'join_lines',
        'Ctrl+L':                          'select_lines',
        'Ctrl+M':                          'hop_brackets',
        'Ctrl+T':                            'print_type',
        'Ctrl+[':                              'unindent',
        'Ctrl+]':                                'indent',
        'Enter':                         'return_handler',
        'Return':                        'return_handler',
        '\"':                                 'wrap_text',
        '\'':                                 'wrap_text',
        ')':                                  'wrap_text',
        '(':                                  'wrap_text',
        '[':                                  'wrap_text',
        ']':                                  'wrap_text',
        '\}':                                 'wrap_text',
        '\{':                                 'wrap_text',
        'Shift+{':                            'wrap_text',
        'Shift+}':                            'wrap_text',
        'Ctrl+Alt+Return':               'new_line_below',
        'Ctrl+Tab':                            'next_tab',
        'Shift+Tab':                           'unindent',
        'Shift+Backtab':                       'unindent',
        'Ctrl+Shift+Up':                  'move_lines_up',
        'Ctrl+Shift+Del':         'delete_to_end_of_line',
        'Ctrl+Shift+K':                    'delete_lines',
        'Ctrl+Shift+Tab':                  'previous_tab',
        'Ctrl+Shift+Backtab':              'previous_tab',
        'Ctrl+Shift+M':         'select_between_brackets',
        'Ctrl+Shift+F':                    'search_input',
        'Ctrl+Shift+D':                 'duplicate_lines',
        'Ctrl+Shift+Return':             'new_line_above',
        'Ctrl++':                               'zoom_in',
        'Ctrl+-':                              'zoom_out',
        'Ctrl+/':                        'comment_toggle',
        'Ctrl+Shift+Backspace': 'delete_to_start_of_line',
        'Ctrl+=':                               'zoom_in',
        'Ctrl+Shift+Down':              'move_lines_down',
    }
}


def load_config(shortcut_config_path):
    with open(shortcut_config_path, 'rt') as f:
        # load json as str, not unicode
        return json_load_byteified(f)

def save_config(config_dict, shortcut_config_path):
    cfg = json.dumps(config_dict, indent=4)
    with open(shortcut_config_path, 'wt') as f:
        f.write(cfg)

# load user config
user_config = load_config(shortcut_config_path)
# SHORTCUT_CONFIG.update(**user_config)


event_types = (QtCore.QEvent.KeyPress,
               QtCore.QEvent.KeyRelease,
               QtCore.QEvent.ShortcutOverride)


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

modmap = {
    QtCore.Qt.Key_Control: QtCore.Qt.ControlModifier,
    QtCore.Qt.Key_Shift: QtCore.Qt.ShiftModifier,
    QtCore.Qt.Key_Alt: QtCore.Qt.AltModifier,
    QtCore.Qt.Key.Key_Meta: QtCore.Qt.MetaModifier,
}

editor_shortcuts = config_dict['editor_shortcuts'].items()
register = {shortcut:getattr(shortcut_functions, function_name)
    for shortcut, function_name in editor_shortcuts}

from pprint import pprint
pprint(register)


class Shortcuts(QtCore.QObject):
    keylist = []

    def __init__(self, widget, register):
        super(Shortcuts, self).__init__()
        self.widget = widget
        self.register = register
        self.widget.installEventFilter(self)
        self.widget.destroyed.connect(self.deleteLater)

    def eventFilter(self, obj, event):
        if not self.widget.hasFocus():
            return False

        if event.type() == QtCore.QEvent.KeyPress:
            combo = self.key_press(event)
            func = self.register.get(combo, None)
            if func is None:
                return False

            print combo, func
            event.accept()
            try:
                func(self.widget)
            except TypeError:
                func(self.widget, event.text())
            return True

        if event.type() == QtCore.QEvent.KeyRelease:
            self.keyseq = QtGui.QKeySequence()
            self.key_release(event)

        return False

    def key_press(self, event):
        key = event.key()
        key = modmap.get(key, key)
        self.keylist.append(key)

        combo = 0
        for k in self.keylist:
            combo |= k

        combo = QtGui.QKeySequence(combo).toString()
        return combo

    def key_release(self, event):
        key = event.key()
        key = modmap.get(key, key)
        try:
            self.keylist.remove(key)
        except ValueError:
            pass


def main():

    app = QtWidgets.QApplication([])
    widget = QtWidgets.QPlainTextEdit()
    # register = get_register(widget, 'editor_shortcuts')
    shortcut_filter = Shortcuts(widget, register)
    # Shortcuts(widget, register)
    # apply_shortcut_register(widget)
    widget.show()
    widget.setPlainText("print 'anus'")

    app.exec_()


if __name__ == '__main__':
    main()




# QtGui.QKeySequence(shortcut)
