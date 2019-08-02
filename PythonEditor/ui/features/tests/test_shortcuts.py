"""
Test that each shortcut registered under an action
produces the desired result.
"""

import __main__
import pytest
from PythonEditor.ui.ide import IDE
from PythonEditor.ui.Qt.QtCore import Qt
from PythonEditor.ui.Qt.QtGui import QKeySequence
from PythonEditor.ui.Qt.QtWidgets import QApplication
from PythonEditor.ui.Qt.QtTest import QTest
from PythonEditor.ui.features import actions


def get_key_from_shortcut(s):
    """
    Get a Qt.Key value from string s.
    """
    if s.endswith('++'):
        p = '+'
    else:
        p = s.split('+').pop()

    k = QKeySequence(p)
    for ky in Qt.Key.values.values():
        if ky == k[0]:
            break
    return ky


def shortcut_to_key_and_modifiers(shortcut):
    """
    Given a shortcut string (e.g. Ctrl+Alt+K)
    convert it into a (key, modifiers) tuple.
    """
    shortcut = shortcut.strip()
    # find the relevant key for the part
    ky = get_key_from_shortcut(shortcut)

    shortcut = shortcut.lower()
    modifiers = Qt.NoModifier
    if 'ctrl' in shortcut:
        modifiers |= Qt.ControlModifier
    if 'shift' in shortcut:
        modifiers |= Qt.ShiftModifier
    if 'alt' in shortcut:
        modifiers |= Qt.AltModifier
    if 'meta' in shortcut:
        modifiers |= Qt.MetaModifier

    return (ky, modifiers)


# method/action names,
# their test and selected text
# and expected results
METHOD_RESULTS_DICT = {
  "delete_lines": {
    "input_text": "some_text"
  },
  "exec_handler": {
    "input_text": "test_editor.clear()"
  },
  "move_to_bottom": {
    "input_text": "next thing\nword new\n",
    "selected_text": "next thing",
    "expected_result": "\nword new\nnext thing",
  },
  "indent": {
    "input_text": "text",
    "expected_result": "    text",
  },
  "delete_to_end_of_line": {
    "input_text": "some_text",
    "expected_result": "some_",
  },
  "return_handler": {
    "input_text": "if this:",
    "expected_result": "if this:\n    ",
  },
  "toggle_backslashes": {
    "input_text": "C:/path/file.txt",
    "expected_result": "C:\\\\path\\\\file.txt",
  },
  "cut_line": {
    "input_text": "some_text",
    "selected_text": "text",
    "expected_result": "some_",
    "cursor_placement": 5,
  },
  "move_to_top": {
    "input_text": "\nword new\nnext thing",
    "selected_text": "next thing",
    "expected_result": "next thing\nword new\n",
  },
  "new_line_above": {
    "input_text": "text",
    "expected_result": "'ntext",
  },
  "toggle_comment": {
    "input_text": "# thing",
    "expected_result": "thing",
  },
  "tab_handler": {
    "input_text": "text",
    "selected_text": "te",
    "expected_result": "    text",
  },
  "unindent": {
    "input_text": "    text",
    "expected_result": "text",
  },
  "duplicate_lines": {
    "input_text": "some_text",
    "expected_result": "some_text'nsome_text",
  },
  "join_lines": {
    "input_text": "text\ntext",
    "expected_result": "texttext",
    "cursor_placement": 4,
  },
  "exec_current_line": {
    "input_text": "test_editor.clear()"
  },
  "copy_block_or_selection": {
    "input_text": "some_text",
    "expected_result": "some_text",
  },
  "delete_to_start_of_line": {
    "input_text": "some_text",
    "expected_result": "text",
    "cursor_placement": 5,
  },
  "new_line_below": {
    "input_text": "text",
    "expected_result": "text\n",
    "cursor_placement": 1,
  },
  "wrap_text": {}, # fuck this one's going to vary per shortcut!
  #   "input_text": "thing",
  #   "expected_result": "'thing'",
  #   "selected_text": "thing"
  # },

  # Not yet tested (and not text-related)
  "goto_definition": {},
  "export_selected_to_external_editor": {},
  "export_current_tab_to_external_editor": {},
  "export_all_tabs_to_external_editor": {},
  "backup_pythoneditor_history": {},
  "zoom_in": {},
  "move_blocks_up": {},
  "fullscreen_editor": {},
  "hop_between_brackets": {},
  "goto_last_position": {},
  "save": {},
  "find_and_replace": {},
  "duplicate_cursor_down": {},
  "save_selected_text": {},
  "open_module_directory": {},
  "move_blocks_down": {},
  "duplicate_cursor_up": {},
  "jump_to_start": {},
  "select_word": {},
  "goto_line": {},
  "reload_package": {},
  "open_module_file": {},
  "print_type": {},
  "command_palette": {},
  "select_between_brackets": {},
  "zoom_out": {},
  "save_as": {},
  "show_shortcuts": {},
  "print_help": {},
  "find": {},
  "show_about": {},
  "escape_handler": {},
  "clear_output": {},
  "open": {},
  "select_lines": {},
  "show_preferences": {},
}


def test_all_methods_accounted_for():
    action_dict = actions.load_actions_from_json()
    editor_actions = action_dict['editor']
    missing = []
    for action in editor_actions.values():
        name = action['Method']
        if name not in METHOD_RESULTS_DICT:
            missing.append(name)
            print '  "'+name+'": {},'
    assert not missing


def test_modifier_keys():
    assert Qt.Modifier.CTRL  == Qt.ControlModifier
    assert Qt.Modifier.SHIFT == Qt.ShiftModifier
    assert Qt.Modifier.META  == Qt.MetaModifier
    assert Qt.Modifier.ALT   == Qt.AltModifier


def run_ascii_shortcut(
        widget=None,
        shortcut='',
        input_text='',
        expected_result='',
        selected_text=None,
        cursor_placement=None,
    ):
    if not shortcut:
        raise Exception('A shortcut is required for this function')
    key, modifiers = shortcut_to_key_and_modifiers(shortcut)
    return run_shortcut(
        widget,
        key,
        modifiers,
        input_text,
        expected_result,
        selected_text=selected_text,
        cursor_placement=cursor_placement,
    )


def setup_for_shortcut(
    widget,
    input_text,
    selected_text=None,
    cursor_placement=None
):
    widget.clear()
    # if widget is editor:
    widget.insertPlainText(input_text)
    widget.activateWindow()
    widget.setFocus(Qt.MouseFocusReason)
    if selected_text is not None:
        doc = widget.document()
        cursor = doc.find(selected_text)
        widget.setTextCursor(cursor)
    if cursor_placement is not None:
        cursor = widget.textCursor()
        cursor.setPosition(cursor_placement)
        widget.setTextCursor(cursor)


def run_shortcut(
        widget,
        key,
        modifiers,
        input_text='',
        expected_result='',
        selected_text=None,
        cursor_placement=None,
    ):
    """
    Test widget of type QPlainTextEdit (or subclass)
    with key of type QtCore.Qt.Key and modifiers of
    type QtCore.Qt.KeyboardModifier. input_text (str or
    unicode) specifies the text the widget will have
    before the key is pressed, and expected_result is a
    unicode string representing the text the widget
    should have after pressing the key.
    """
    app = QApplication.instance()
    window = app.activeWindow()

    setup_for_shortcut(
        widget,
        input_text,
        selected_text=selected_text,
        cursor_placement=cursor_placement
    )

    QTest.keyPress(
        widget,
        key,
        modifiers
    )

    text = widget.toPlainText()
    window.activateWindow()
    return text


@pytest.fixture()
def editor(qtbot):
    ide = IDE()
    ide.show()
    qtbot.addWidget(ide)
    qtbot.waitForWindowShown(ide)
    editor = ide.python_editor.editor
    return editor


def test_editor_delete_lines(editor):
    for shortcut in [u'Ctrl+Shift+K']:
        editor_text = run_ascii_shortcut(
            widget=editor,
            shortcut=shortcut,
            input_text='some_text'
        )
        assert editor_text == u''

def test_editor_cut_line(editor):
    for shortcut in [u'Ctrl+X']:
        editor_text = run_ascii_shortcut(
            widget=editor,
            shortcut=shortcut,
            input_text='some_text',
            selected_text=u'text',
            expected_result=u'some_'
        )
        assert editor_text == u'some_'

def test_editor_indent(editor):
    for shortcut in [u'Ctrl+]']:
        editor_text = run_ascii_shortcut(
            widget=editor,
            shortcut=shortcut,
            input_text='text',
            expected_result=u'    text'
        )
        assert editor_text == u'    text'

def test_editor_tab_handler(editor):
    for shortcut in [u'Tab']:
        editor_text = run_ascii_shortcut(
            widget=editor,
            shortcut=shortcut,
            input_text='text',
            selected_text='te',
            expected_result=u'    text'
        )
        assert editor_text == u'    text'

def test_editor_wrap_text(editor):
    editor_text = run_ascii_shortcut(
        widget=editor,
        shortcut='"',
        input_text='thing',
        selected_text='thing',
        expected_result='"thing"'
    )
    assert editor_text == '"thing"'

    editor_text = run_ascii_shortcut(
        widget=editor,
        shortcut="'",
        input_text='thing',
        selected_text='thing',
        expected_result="'thing'"
    )
    assert editor_text == "'thing'"

    editor_text = run_ascii_shortcut(
        widget=editor,
        shortcut='[',
        input_text='thing',
        selected_text='thing',
        expected_result='[thing]'
    )
    assert editor_text == '[thing]'

    editor_text = run_ascii_shortcut(
        widget=editor,
        shortcut=']',
        input_text='thing',
        selected_text='thing',
        expected_result='[thing]'
    )
    assert editor_text == '[thing]'

    editor_text = run_ascii_shortcut(
        widget=editor,
        shortcut='(',
        input_text='thing',
        selected_text='thing',
        expected_result='(thing)'
    )
    assert editor_text == '(thing)'

    editor_text = run_ascii_shortcut(
        widget=editor,
        shortcut=')',
        input_text='thing',
        selected_text='thing',
        expected_result='(thing)'
    )
    assert editor_text == '(thing)'

    editor_text = run_ascii_shortcut(
        widget=editor,
        shortcut='{',
        input_text='thing',
        selected_text='thing',
        expected_result='{thing}'
    )
    assert editor_text == '{thing}'

    editor_text = run_ascii_shortcut(
        widget=editor,
        shortcut='}',
        input_text='thing',
        selected_text='thing',
        expected_result='{thing}'
    )
    assert editor_text == '{thing}'


def test_editor_copy_block_or_selection(editor):
    for shortcut in [u'Ctrl+C']:
        editor_text = run_ascii_shortcut(
            widget=editor,
            shortcut=shortcut,
            input_text='some_text',
            expected_result=u'some_text'
        )
        assert editor_text == u'some_text'

def test_editor_return_handler(editor):
    for shortcut in [u'Return', u'Enter', u'Alt+Enter', u'Alt+Return']:
        editor_text = run_ascii_shortcut(
            widget=editor,
            shortcut=shortcut,
            input_text='if this:',
            expected_result=u'if this:\n    '
        )
        assert editor_text == u'if this:\n    '

def test_editor_move_to_bottom(editor):
    for shortcut in [u'Ctrl+Alt+End']:
        editor_text = run_ascii_shortcut(
            widget=editor,
            shortcut=shortcut,
            input_text='next thing\nword new\n',
            selected_text='next thing',
            expected_result=u'\nword new\nnext thing'
        )
        assert editor_text == u'\nword new\nnext thing'

def test_editor_toggle_comment(editor):
    for shortcut in [u'Ctrl+/']:
        editor_text = run_ascii_shortcut(
            widget=editor,
            shortcut=shortcut,
            input_text='#thing',
            expected_result=u'thing'
        )
        assert editor_text == u'thing'

def test_editor_new_line_below(editor):
    for shortcut in [u'Ctrl+Alt+Return']:
        editor_text = run_ascii_shortcut(
            widget=editor,
            shortcut=shortcut,
            input_text='text',
            expected_result=u'text\n',
            cursor_placement=1
        )
        assert editor_text == u'text\n'

def test_editor_unindent(editor):
    for shortcut in [u'Ctrl+[', u'Shift+Tab', u'Shift+Backtab']:
        editor_text = run_ascii_shortcut(
            widget=editor,
            shortcut=shortcut,
            input_text='    text',
            expected_result=u'text'
        )
        assert editor_text == u'text'

def test_editor_exec_current_line(editor):
    __main__.__dict__['test_editor'] = editor
    for shortcut in [u'Ctrl+B']:
        editor_text = run_ascii_shortcut(
            widget=editor,
            shortcut=shortcut,
            input_text='test_editor.clear()'
        )
        assert editor_text == u''

def test_editor_exec_handler(editor):
    __main__.__dict__['test_editor'] = editor
    for shortcut in [u'Ctrl+Enter', u'Ctrl+Return']:
        editor_text = run_ascii_shortcut(
            widget=editor,
            shortcut=shortcut,
            input_text='test_editor.clear()'
        )
        assert editor_text == u''

def test_editor_join_lines(editor):
    for shortcut in [u'Ctrl+J']:
        editor_text = run_ascii_shortcut(
            widget=editor,
            shortcut=shortcut,
            input_text='text\ntext',
            expected_result=u'texttext',
            cursor_placement=4
        )
        assert editor_text == u'texttext'

def test_editor_duplicate_lines(editor):
    for shortcut in [u'Ctrl+Shift+D']:
        editor_text = run_ascii_shortcut(
            widget=editor,
            shortcut=shortcut,
            input_text='some_text',
            expected_result=u"some_text\nsome_text"
        )
        assert editor_text == u"some_text\nsome_text"

def test_editor_delete_to_start_of_line(editor):
    for shortcut in [u'Ctrl+Shift+Backspace']:
        editor_text = run_ascii_shortcut(
            widget=editor,
            shortcut=shortcut,
            input_text='some_text',
            expected_result=u'text',
            cursor_placement=5
        )
        assert editor_text == u'text'

def test_editor_toggle_backslashes(editor):
    for shortcut in [u'Ctrl+\\']:
        editor_text = run_ascii_shortcut(
            widget=editor,
            shortcut=shortcut,
            input_text='C:/path/file.txt',
            expected_result=u'C:\\\\path\\\\file.txt'
        )
        assert editor_text == u'C:\\\\path\\\\file.txt'

def test_editor_move_to_top(editor):
    for shortcut in [u'Ctrl+Alt+Home']:
        editor_text = run_ascii_shortcut(
            widget=editor,
            shortcut=shortcut,
            input_text='\nword new\nnext thing',
            selected_text='next thing',
            expected_result=u'next thing\nword new\n'
        )
        assert editor_text == u'next thing\nword new\n'

def test_editor_new_line_above(editor):
    for shortcut in [u'Ctrl+Shift+Return']:
        editor_text = run_ascii_shortcut(
            widget=editor,
            shortcut=shortcut,
            input_text='text',
            expected_result=u"\ntext"
        )
        assert editor_text == u"\ntext"

def test_editor_delete_to_end_of_line(editor):
    for shortcut in [u'Ctrl+Shift+Del']:
        editor_text = run_ascii_shortcut(
            widget=editor,
            shortcut=shortcut,
            input_text='some_text',
            expected_result=u'some_',
            cursor_placement=5
        )
        assert editor_text == u'some_'




