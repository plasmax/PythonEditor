import subprocess
from PythonEditor.ui.Qt import QtWidgets, QtGui, QtCore
from constants import NUKE_DIR, SUBLIME_PATH

def save_selected_text(editor):
    path, _ = QtWidgets.QFileDialog.getSaveFileName(
        editor, 
        'Save Selected Text', 
        NUKE_DIR, 
        selectedFilter='*.py')

    print(path)

    if path:
        text = editor.textCursor().selection().toPlainText()
        with open(path, 'w') as f:
            f.write(text)
    return path

def export_selected_to_sublime(editor):
    path = save_selected_text(editor)
    if path:
        subprocess.Popen([SUBLIME_PATH, path])
