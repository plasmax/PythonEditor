from __future__ import print_function
import os
import subprocess

from PythonEditor.ui.Qt import QtWidgets
from PythonEditor.utils import constants


def write_to_file(path, text):
    """
    Write text to a file.
    """
    with open(path, 'w') as f:
        try:
            f.write(text)
        except UnicodeEncodeError:
            f.write(text.encode('utf-16'))


def get_save_file_name(editor, title='Save Text As'):
    """
    Ask user where they would like to save.

    :return: Path user chose to save. None if user cancels.
    """
    path, _ = QtWidgets.QFileDialog.getSaveFileName(
        editor,
        title,
        constants.NUKE_DIR,
        selectedFilter='*.py')

    if not path:
        path = None

    return path


def save(editor):
    """
    Look for a file path property on the editor
    and save the entire document to that file.

    Sets the read_only status of the editor to True,
    meaning the autosave will consider it removable
    if the tab is closed.
    """
    if not hasattr(editor, 'path'):
        path = save_as(editor)
        if path is None:
            # User cancelled
            return

    write_to_file(editor.path, editor.toPlainText())
    editor.read_only = True
    print('Saved', editor.path, sep=' ')
    editor.contents_saved_signal.emit(editor)
    return editor.path


def save_as(editor):
    """
    Ask the user where they would like to save the document.
    """
    path = get_save_file_name(editor, title='Save As')
    if path:
        editor.path = path
        save(editor)
    return path


def save_selected_text(editor):
    """
    Export whatever text we have selected to a file. It's only
    in this case that we don't want to change the autosave or
    set the editor status to read_only, because we may be saving
    only part of the document.
    """
    text = editor.textCursor().selection().toPlainText()
    path = get_save_file_name(editor, title='Save Selected Text')
    if path:
        write_to_file(path, text)
    return path


def export_selected_to_external_editor(editor):
    path = save_selected_text(editor)

    #TODO: this is a horrible hack to avoid circular imports
    from PythonEditor.ui.features.autosavexml import get_external_editor_path
    EXTERNAL_EDITOR_PATH = get_external_editor_path()

    if path and EXTERNAL_EDITOR_PATH:
        subprocess.Popen([EXTERNAL_EDITOR_PATH, path])
    return path


def save_editor(folder, name, editor):
    """
    Compose a path from folder and editor name.
    Set the editor path property, then save.
    """
    file = name.split('.')[0] + '.py'
    editor.path = os.path.join(folder, file)
    save(editor)
    return editor.path


def open_external_editor(path):

    #TODO: this is a horrible hack to avoid circular imports
    from PythonEditor.ui.features.autosavexml import get_external_editor_path
    EXTERNAL_EDITOR_PATH = get_external_editor_path()

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
