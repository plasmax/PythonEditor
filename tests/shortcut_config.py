"""
Rationale: allow users to override the config
using custom json files that list function names
paired with key sequences.
"""
import imp
import shortcut_functions


path = 'C:/Repositories/PythonEditor/PythonEditor/ui/Qt.py'
Qt = imp.load_source('Qt', path)
QtWidgets, QtGui, QtCore = Qt.QtWidgets, Qt.QtGui, Qt.QtCore

# put this in a config
# if user config exists, load it and update this dict
# changing user prefs sets keys
SHORTCUT_CONFIG = {
    'editor_shortcuts': {
                     'exec_current_line': 'Ctrl+B',
                     'new_line_above': 'Ctrl+Shift+Return',
                     'new_line_below': 'Ctrl+Alt+Return',
                     'duplicate_lines': 'Ctrl+Shift+D',
                     'print_help': 'Ctrl+H',
                     'print_type': 'Ctrl+T',
                     'search_input': 'Ctrl+Shift+F',
                     'select_lines': 'Ctrl+L',
                     'join_lines': 'Ctrl+J',
                     'comment_toggle': 'Ctrl+/',
                     'indent': 'Ctrl+]',
                     'unindent': ('Ctrl+[', 'Shift+Tab'),
                     'next_tab': 'Ctrl+Tab',
                     'previous_tab': 'Ctrl+Shift+Tab',
                     'zoom_in': ('Ctrl+=', 'Ctrl++'),
                     'zoom_out': 'Ctrl+-',
                     'delete_lines': 'Ctrl+Shift+K',
                     'select_word': 'Ctrl+D',
                     'hop_brackets': 'Ctrl+M',
                     'select_between_brackets': 'Ctrl+Shift+M',
                     'delete_to_end_of_line': 'Ctrl+Shift+Delete',
                     'delete_to_start_of_line': 'Ctrl+Shift+Backspace',
                     'move_lines_up': 'Ctrl+Shift+Up',
                     'move_lines_down': 'Ctrl+Shift+Down',
                     'wrap_text': ('\'', '"', '(', ')', '[', ']', '\{', '\}'),
                     'return_handler': ('Return', 'Enter'),
                     # 'clear_output_signal.emit': 'Ctrl+Backspace',
                     # 'Ctrl+Shift+Alt+Up': notimp('duplicate cursor up'),
                     # 'Ctrl+Shift+Alt+Down': notimp('duplicate cursor down'),
                     },
    'tab_shortcuts': {
                     'editortabs.new_tab': 'Ctrl+Shift+N',
                     'editortabs.close_current_tab': 'Ctrl+Shift+W',
                     # 'reopen_previous_tab': 'Ctrl+Shift+T',
                     },
    'signal_dict': {
                    'tab_handler': 'Tab',
                    'return_handler': 'Return/Enter',
                    # 'wrap_text': r'\' " ( ) [ ] \{ \}',
                    'wrap_text': ('\'', '"', '(', ')', '[', ']', '\{', '\}'),
                    'move_to_top': 'Ctrl+Alt+Home',
                    'move_to_bottom': 'Ctrl+Alt+End',
                    'cut_line': 'Ctrl+X',
                    'jump_to_start': 'Home',
                    'wheel_zoom': 'Ctrl+Mouse Wheel',
                    'clear_output_signal': 'Ctrl+Backspace',
                    }
}

event_types = (QtCore.QEvent.KeyPress,
               QtCore.QEvent.KeyRelease,
               QtCore.QEvent.ShortcutOverride)

SHIFT = QtCore.Qt.ShiftModifier
CTRL = QtCore.Qt.ControlModifier
ALT = QtCore.Qt.AltModifier

mods = {
    QtCore.Qt.Key_Control: CTRL,
    QtCore.Qt.Key_Shift: SHIFT,
    QtCore.Qt.Key_Alt: ALT,
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
