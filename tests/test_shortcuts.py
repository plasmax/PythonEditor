"""
This suite of tests are the definitive tests for all default shortcuts
placed on the editor. The function test_shortcut is the primary test
mechanism, with an input and expected output.
Testing per action is also done in case the user changes the action shortcut.
"""
import json
import time
from pprint import pprint

from Qt import QtWidgets, QtGui, QtCore, QtTest
from PythonEditor.ui import editor
from PythonEditor.ui.features import actions


def get_shortcuts():
    action_dict = actions.load_actions_from_json()
    shortcuts = []
    for widget_name, widget_actions in action_dict.items():
        for name, attributes in widget_actions.items():
            strokes = attributes['Shortcuts']
            for shortcut in strokes:
                shortcuts.append(shortcut)
    return shortcuts


def get_key_from_shortcut(s):
    if s.endswith('++'):
        p = '+'
    else:
        p = s.split('+').pop()

    k = QtGui.QKeySequence(p)
    for ky in QtCore.Qt.Key.values.values():
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
    modifiers = QtCore.Qt.NoModifier
    if 'ctrl' in shortcut:
        modifiers |= QtCore.Qt.ControlModifier
    if 'shift' in shortcut:
        modifiers |= QtCore.Qt.ShiftModifier
    if 'alt' in shortcut:
        modifiers |= QtCore.Qt.AltModifier
    if 'meta' in shortcut:
        modifiers |= QtCore.Qt.MetaModifier

    return (ky, modifiers)


def test_ascii_shortcut(
        widget=None,
        shortcut='',
        input_text='',
        expected_result='',
        selected_text=None,
        cursor_placement=None,
    ):
    key, modifiers = shortcut_to_key_and_modifiers(shortcut)
    test_shortcut(
        widget,
        key,
        modifiers,
        input_text,
        expected_result,
        selected_text=selected_text,
        cursor_placement=cursor_placement,
    )


def setup_test(
    widget, 
    input_text, 
    selected_text=None, 
    cursor_placement=None
):
    widget.clear()
    widget.insertPlainText(input_text)
    widget.activateWindow()
    widget.setFocus(QtCore.Qt.MouseFocusReason)
    if selected_text is not None:
        doc = widget.document()
        cursor = doc.find(selected_text)
        widget.setTextCursor(cursor)
    if cursor_placement is not None:
        cursor = widget.textCursor()
        cursor.setPosition(cursor_placement)
        widget.setTextCursor(cursor)
        

def test_shortcut(
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
    app = QtWidgets.QApplication.instance()
    window = app.activeWindow()

    try:
        setup_test(
            widget, 
            input_text, 
            selected_text=selected_text, 
            cursor_placement=cursor_placement
        )

        QtTest.QTest.keyPress(
            widget,
            key,
            modifiers
        )

        text = widget.toPlainText()
        assert text == expected_result
    except AssertionError:
        shortcut = QtGui.QKeySequence(key | modifiers).toString()
        print('test for %r failed to produce result %r with input %r. produced %r instead' % (
            shortcut,
            expected_result,
            input_text,
            text
            )
        )
    finally:
        window.activateWindow()


def test_action(
    widget,
    action_name,
    input_text,
    expected_result,
    selected_text=None,
    cursor_placement=None
):
    """
    Sets the widget text and applies the action,
    given by name, to the text.
    """
    app = QtWidgets.QApplication.instance()
    window = app.activeWindow()

    for action in widget.actions():
        if action.text() == action_name:
            break

    assert action_name == action.text()

    try:
        setup_test(
            widget, 
            input_text, 
            selected_text=selected_text, 
            cursor_placement=cursor_placement
        )

        # widget.last_key_pressed may be necessary here for some actions... but should those actions really fall under this domain? or be placed on the editor?
        action.trigger()

        text = widget.toPlainText()
        assert text == expected_result
    except AssertionError:
        raise
    finally:
        window.activateWindow()

#&&
assert QtCore.Qt.Modifier.ALT == QtCore.Qt.AltModifier
assert QtCore.Qt.Modifier.CTRL == QtCore.Qt.ControlModifier
assert QtCore.Qt.Modifier.SHIFT == QtCore.Qt.ShiftModifier
assert QtCore.Qt.Modifier.META == QtCore.Qt.MetaModifier

for s in get_shortcuts():
    print '\n',s
    print shortcut_to_key_and_modifiers(s)


#&&

for s in get_shortcuts():
    k = QtGui.QKeySequence(s)[0]
    ky = get_key_from_shortcut(s)
    if ky is None:
        raise Exception('No key found for %s' % s)

    for mod in QtCore.Qt.Modifier.values.values():
        if mod & ky == k:
            print mod, ky, k

#&&
pprint(actions.load_actions_from_json())
#&& # actual tests begin here.
    # TODO: there will be tests that require selecting text, as well.
test_editor = editor.Editor()
test_editor.show()

QtTest.QTest.qWaitForWindowShown(test_editor)

test_ascii_shortcut(
    widget=test_editor,
    shortcut='Alt+Return',
    input_text='if this:',
    expected_result=u'if this:\n    ',
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut='Alt+Enter',
    input_text='if this:',
    expected_result=u'if this:\n    ',
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut='Enter',
    input_text='if this:',
    expected_result=u'if this:\n    ',
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut='Return',
    input_text='if this:',
    expected_result=u'if this:\n    ',
)

# for this one we need to test what's in the clipboard
test_ascii_shortcut(
    widget=test_editor,
    shortcut='Ctrl+C',
    input_text='some_text',
    expected_result=u'some_text',
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut='Ctrl+X',
    input_text='some_text',
    expected_result=u'',
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut='Ctrl+X',
    input_text='some_text',
    expected_result=u'some_',
    selected_text=u'text'
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut='Ctrl+Shift+K',
    input_text='some_text',
    expected_result=u'',
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut='Ctrl+Shift+Del',
    input_text='some_text',
    expected_result=u'some_',
    cursor_placement=5
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut='Ctrl+Shift+Backspace',
    input_text='some_text',
    expected_result=u'text',
    cursor_placement=5
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut='Ctrl+Shift+D',
    input_text='some_text',
    expected_result=u'some_text\nsome_text',
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut='Ctrl+Enter',
    input_text='test_editor.clear()',
    expected_result=u'',
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut='Ctrl+Return',
    input_text='test_editor.clear()',
    expected_result=u'',
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut='Ctrl+B',
    input_text='test_editor.clear()',
    expected_result=u'',
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut='Ctrl+]',
    input_text='text',
    expected_result=u'    text',
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut='Ctrl+[',
    input_text='    text',
    expected_result=u'text',
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut='Shift+Tab',
    input_text='    text',
    expected_result=u'text',
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut='Shift+Backtab',
    input_text='    text',
    expected_result=u'text',
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut='Ctrl+J',
    input_text='text\ntext',
    expected_result=u'texttext',
    cursor_placement=4,
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut='Ctrl+Shift+Return',
    input_text='text',
    expected_result=u'\ntext',
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut='Ctrl+Alt+Return',
    input_text='text',
    expected_result=u'text\n',
    cursor_placement=1,
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut='Tab',
    input_text='text',
    expected_result=u'    text',
    selected_text='te'
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut='Ctrl+Alt+Home',
    input_text='\nword new\nnext thing',
    expected_result=u'next thing\nword new\n',
    selected_text='next thing'
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut='Ctrl+Alt+End',
    input_text='next thing\nword new\n',
    expected_result=u'\nword new\nnext thing',
    selected_text='next thing'
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut='Ctrl+\\',
    input_text='C:\\path\\file.txt',
    expected_result=u'C:/path/file.txt',
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut='Ctrl+\\',
    input_text='C:/path/file.txt',
    expected_result=u'C:\\\\path\\\\file.txt',
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut='Ctrl+/',
    input_text='thing',
    expected_result=u'#thing',
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut='Ctrl+/',
    input_text='#thing',
    expected_result=u'thing',
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut='"',
    input_text='thing',
    expected_result=u'"thing"',
    selected_text='thing'
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut='[',
    input_text='thing',
    expected_result=u'[thing]',
    selected_text='thing'
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut=']',
    input_text='thing',
    expected_result=u'[thing]',
    selected_text='thing'
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut='(',
    input_text='thing',
    expected_result=u'(thing)',
    selected_text='thing'
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut=')',
    input_text='thing',
    expected_result=u'(thing)',
    selected_text='thing'
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut='{',
    input_text='thing',
    expected_result=u'{thing}',
    selected_text='thing'
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut='}',
    input_text='thing',
    expected_result=u'{thing}',
    selected_text='thing'
)

test_ascii_shortcut(
    widget=test_editor,
    shortcut="'",
    input_text='thing',
    expected_result=u"'thing'",
    selected_text='thing'
)

#&& # a few more
'Ctrl+Shift+Down'
'Ctrl+Shift+Up'

#&&

def test_shortcuts(editor):
    """
    Test all shortcuts in one go.
    Originally designed to simply test whether the keypress
    event was received.
    """

    editor.setFocus(
        QtCore.Qt.MouseFocusReason
    )
    if not editor.hasFocus():
        raise Exception(
            'Need an editor visible to test'
        )

    shortcuts = get_shortcuts()
    for shortcut in shortcuts:
        modifiers = QtCore.Qt.NoModifier
        shortcut = shortcut.strip()

        seq = shortcut.split('+')
        if shortcut.endswith('+'):
            letter = '+'
        for part in seq:
            part = part.strip()
            if not part:
                continue
            if part.lower()   == 'ctrl':
                modifiers |= QtCore.Qt.ControlModifier
            elif part.lower() == 'shift':
                modifiers |= QtCore.Qt.ShiftModifier
            elif part.lower() == 'alt':
                modifiers |= QtCore.Qt.AltModifier
            elif part.lower() == 'meta':
                modifiers |= QtCore.Qt.MetaModifier
            else:
                # only allow one part for now
                letter = part

        # find the relevant key for the part
        if letter == 'Del':
            letter = 'Delete'
        lookup = 'Key_'+letter
        ky = QtCore.Qt.Key.values.get(lookup)
        if ky is None:
            ky = QtTest.QTest.asciiToKey(letter)
            print 'failed to find %s, using %s' % (lookup, ky)

        combo = ky | modifiers
        print '#----------------------'
        print 'translated:', QtGui.QKeySequence(combo).toString()
        print '\nTesting:', shortcut, ky

        editor.setFocus(
            QtCore.Qt.MouseFocusReason
        )
        QtTest.QTest.keyPress(
            editor,
            ky,
            modifiers
        )
        editor.setFocus(
            QtCore.Qt.MouseFocusReason
        )

        #TODO: here is where we test for input vs expected result.
        print '#------------',
        if not COMBO_FOUND:
            print 'KEY NOT WORKING!'
            raise Exception('KEY NOT WORKING!')
        else:
            print 'passed.'

