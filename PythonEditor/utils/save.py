from __future__ import print_function
import subprocess
from PythonEditor.ui.Qt import QtWidgets, QtGui, QtCore
from constants import NUKE_DIR, SUBLIME_PATH

def save_text(editor, text):
    """
    TODO:
    Is this better placed in filehandling? It generates a UI
    """
    path, _ = QtWidgets.QFileDialog.getSaveFileName(
        editor, 
        'Save Selected Text', 
        NUKE_DIR, 
        selectedFilter='*.py')

    print('Saved', path, sep=' ')

    if path:
        text = editor.textCursor().selection().toPlainText()
        with open(path, 'w') as f:
            f.write(text)
    return path

def save_selected_text(editor):
    text = editor.textCursor().selection().toPlainText()
    save_text(editor, text)

def save_as(editor):
    text = editor.toPlainText()
    save_text(editor, text)

def export_selected_to_sublime(editor):
    path = save_selected_text(editor)
    if path:
        subprocess.Popen([SUBLIME_PATH, path])
