from PythonEditor.ui.Qt import QtWidgets, QtGui, QtCore
from PythonEditor.utils import save


def toggle_backslashes_in_string(text):
    if '\\' in text:
        text = text.replace('\\\\', '/')
        text = text.replace('\\', '/')
    elif '/' in text:
        text = text.replace('/', '\\')
    return text


def toggle_backslashes(editor):
    textCursor = editor.textCursor()
    selection = textCursor.selection()
    text = selection.toPlainText()
    if not text:
        textCursor.select(QtGui.QTextCursor.BlockUnderCursor)
        text = textCursor.selectedText()

    edited_text = toggle_backslashes_in_string(text)
    if edited_text == text:
        return
    textCursor.insertText(text)


def save_action(tabs, editor):
    """
    """
    path = tabs.get('path')
    text = editor.toPlainText()
    path = save.save(text, path)
    if path is None:
        return
    tabs['path'] = path
    tabs['saved'] = True
    # notify the autosave to empty entry
    tabs.contents_saved_signal.emit(tabs['uuid'])


def open_action(tabs, editor):
    """
    Simple open file.
    :tabs: TabBar
    :editor: Editor
    """
    o = QtWidgets.QFileDialog.getOpenFileName
    path, _ = o(tabs, "Open File")
    if not path:
        return

    with open(path, 'rt') as f:
        text = f.read()

    for index in range(tabs.count()):
        data = tabs.tabData(index)
        if data is None:
            continue

        if data.get('path') != path:
            continue

        # try to avoid more costly 2nd comparison
        if data.get('text') == text:
            tabs.setCurrentIndex(index)
            return

    tab_name = os.path.basename(path)

    # Because the document will be open in read-only mode, the
    # autosave should not save the editor's contents until the
    # contents have been modified.
    data = {
        'uuid'  : str(uuid.uuid4()),
        'name'  : tab_name,
        'text'  : '',
        'path'  : path,
        'date'  : '', # need the file's date
        'saved' : True, # read-only
    }

    tabs.new_tab(tab_name=tab_name)
    editor.setPlainText(text)


# DEFAULT_WIDGET = QtWidgets.QWidget()

# def make_action(callable):
#     global DEFAULT_WIDGET
#     action = QtWidgets.QAction(DEFAULT_WIDGET)
#     action.triggered.connect(callable)
#     return action

# # actions

# actions = {
#     'toggle_backslash_action' : make_action(toggle_backslashes),
#     'save' : make_action(save),
# }

# tests

"""
TEST_TEXT = '''
c:\\path/to\\some\\file.jpg
'''

def test_toggle_backslashes():
    editor = QtWidgets.QPlainTextEdit()
    test_toggle_backslashes.editor = editor
    editor.setPlainText(TEST_TEXT)
    editor.show()
    textCursor = editor.textCursor()
    textCursor.setPosition(0, QtGui.QTextCursor.MoveAnchor)
    editor.setTextCursor(textCursor)
    toggle_backslashes(editor)

TEST_TEXT = toggle_backslashes_in_string(TEST_TEXT)
print TEST_TEXT
test_toggle_backslashes()
"""