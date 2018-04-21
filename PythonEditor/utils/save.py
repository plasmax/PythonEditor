from __future__ import print_function
import os
import subprocess

from PythonEditor.ui.Qt import QtWidgets
from PythonEditor.utils import constants


def save_text(path, text):
    with open(path, 'w') as f:
        f.write(text)


def save_text_as(editor, text, title='Save Text As'):
    """
    TODO:
    Is this better placed in filehandling? It generates a UI
    """
    path, _ = QtWidgets.QFileDialog.getSaveFileName(
        editor,
        title,
        constants.NUKE_DIR,
        selectedFilter='*.py')

    if path:
        print('Saved', path, sep=' ')
        save_text(path, text)
    return path


def save_selected_text(editor):
    text = editor.textCursor().selection().toPlainText()
    return save_text_as(editor, text, title='Save Selected Text')


def save_as(editor):
    text = editor.toPlainText()
    return save_text_as(editor, text, title='Save As')


def export_selected_to_external_editor(editor):
    path = save_selected_text(editor)
    EXTERNAL_EDITOR_PATH = constants.get_external_editor_path()
    if path and EXTERNAL_EDITOR_PATH:
        subprocess.Popen([EXTERNAL_EDITOR_PATH, path])


def save_editor(folder, name, editor):
    text = editor.toPlainText()
    file = name.split('.')[0] + '.py'
    path = os.path.join(folder, file)
    save_text(path, text)


def open_external_editor(path):
    EXTERNAL_EDITOR_PATH = constants.get_external_editor_path()
    if path and EXTERNAL_EDITOR_PATH:
        subprocess.Popen([EXTERNAL_EDITOR_PATH, path])


def export_current_tab_to_external_editor(edittabs):
    widget = edittabs.currentWidget()
    not_editor = (widget.objectName() != 'Editor')
    if not_editor:
        return

    tab_index = edittabs.currentIndex()
    name = edittabs.tabText(tab_index)

    path, _ = QtWidgets.QFileDialog.getSaveFileName(
        edittabs,
        'Choose Directory to save current tab',
        os.path.join(constants.NUKE_DIR, name),
        selectedFilter='*.py')

    if not path:
        return

    editor = widget
    folder = os.path.dirname(path)
    save_editor(folder, name, editor)
    open_external_editor(path)


def export_all_tabs_to_external_editor(edittabs):
    editors = []
    for tab_index in reversed(range(edittabs.count())):
        widget = edittabs.widget(tab_index)
        if widget.objectName() == 'Editor':
            name = edittabs.tabText(tab_index)
            editors.append((tab_index, name, widget))

    if not bool(editors):
        return

    path, _ = QtWidgets.QFileDialog.getSaveFileName(
        edittabs,
        'Choose Directory to save all tabs',
        os.path.join(constants.NUKE_DIR, 'tab_name_used_per_file'),
        selectedFilter='*.py')

    if not path:
        return

    folder = os.path.dirname(path)

    for _, name, editor in editors:
        save_editor(folder, name, editor)

    open_external_editor(folder)

    Yes = QtWidgets.QMessageBox.Yes
    No = QtWidgets.QMessageBox.No
    answer = QtWidgets.QMessageBox.question(
        edittabs,
        'Remove all tabs?',
        'Choosing Yes will remove all tabs and clear the temp file.',
        Yes, No)

    if answer == Yes:
        for tab_index, _, editor in editors:
            editor.setPlainText('')
        edittabs.reset_tab_signal.emit()
