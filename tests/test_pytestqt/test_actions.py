from PythonEditor.ui.features import actions
from PythonEditor.ui.Qt import QtWidgets, QtGui

def test_toggle_backslashes_in_string():
    test_path = "c:\\path/to\\some\\file.jpg"
    result = actions.toggle_backslashes_in_string(test_path)
    assert result == "c:/path/to/some/file.jpg"


def test_toggle_backslashes():
    editor = QtWidgets.QPlainTextEdit()
    test_path = "c:\\path/to\\some\\file.jpg"
    editor.setPlainText(test_path)
    textCursor = editor.textCursor()
    textCursor.setPosition(0, QtGui.QTextCursor.MoveAnchor)
    editor.setTextCursor(textCursor)
    actions.toggle_backslashes(editor)
    assert editor.toPlainText() == "c:/path/to/some/file.jpg"

