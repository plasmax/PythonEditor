from __future__ import print_function
import os
import subprocess
from PythonEditor.ui.Qt import QtWidgets, QtGui, QtCore
from constants import NUKE_DIR

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

    if path:
        print('Saved', path, sep=' ')
        text = editor.textCursor().selection().toPlainText()
        with open(path, 'w') as f:
            f.write(text)
    return path

def save_selected_text(editor):
    text = editor.textCursor().selection().toPlainText()
    return save_text(editor, text)

def save_as(editor):
    text = editor.toPlainText()
    return save_text(editor, text)

def export_selected_to_external_editor(editor):
    path = save_selected_text(editor)
    EXTERNAL_EDITOR_PATH = os.environ.get('EXTERNAL_EDITOR_PATH')
    if path and EXTERNAL_EDITOR_PATH:
        subprocess.Popen([EXTERNAL_EDITOR_PATH, path])
