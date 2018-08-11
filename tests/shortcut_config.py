"""
Rationale: allow users to override the config
using custom json files that list function names
paired with key sequences.
"""

from PythonEditor.ui.Qt import QtWidgets, QtGui, QtCore


SHORTCUT_CONFIG = {
    'editor_shortcuts': {
                     'exec_current_line': 'Ctrl+B',
                     'new_line_above': 'Ctrl+Shift+Return',
                     'new_line_below': 'Ctrl+Alt+Return',
                     'clear_output_signal.emit': 'Ctrl+Backspace',
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
                    'wrap_text': r'\' " ( ) [ ] \{ \}',
                    'move_to_top': 'Ctrl+Alt+Home',
                    'move_to_bottom': 'Ctrl+Alt+End',
                    'cut_line': 'Ctrl+X',
                    'jump_to_start': 'Home',
                    'wheel_zoom': 'Ctrl+Mouse Wheel',
                    'clear_output_signal': 'Ctrl+Backspace',
                    }
}


def map_shortcut_to_function(shortcut, function, widget):
        context = QtCore.Qt.WidgetShortcut
        key_sequence = QtGui.QKeySequence(shortcut)
        qshortcut = QtWidgets.QShortcut(key_sequence,
                                        widget,
                                        function,
                                        context=context)
        qshortcut.setObjectName(shortcut)
