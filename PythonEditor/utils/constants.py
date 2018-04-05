import sys
import os
from xml.etree import ElementTree

pyside = 'PySide'
pyqt = 'PyQt4'

if 'nuke' in globals():
    import nuke
    if nuke.NUKE_VERSION_MAJOR > 10:
        pyside = 'PySide2'
        pyqt = 'PyQt5'

USER = os.environ.get('USERNAME')
NUKE_DIR = os.path.join(os.path.expanduser('~'), '.nuke')
AUTOSAVE_FILE = os.path.join(NUKE_DIR, 'PythonEditorHistory.xml')
QT_VERSION = pyside + os.pathsep + pyqt

def get_editor_xml():
    parser = ElementTree.parse(AUTOSAVE_FILE)
    root = parser.getroot()
    editor_elements = root.findall('external_editor_path')
    return root, editor_elements

def get_external_editor_path():
    """
    Checks the autosave file for an 
    <external_editor_path> element.
    """
    root, editor_elements = get_editor_xml()

    editor_path = None
    if editor_elements:
        editor_element = editor_elements[0] 
        path = editor_element.text
        if path and os.path.isdir( os.path.dirname(path) ):
            editor_path = path

    if editor_path:
        os.environ['EXTERNAL_EDITOR_PATH'] = editor_path
        return editor_path

def set_external_editor_path(path=None):
    """
    Prompts the user for a new
    external editor path. Overrides
    """
    root, editor_elements = get_editor_xml()
    for e in editor_elements:
        root.remove(e)

    if not path:
        from PythonEditor.ui.Qt import QtWidgets
        dialog = QtWidgets.QInputDialog()
        results = QtWidgets.QInputDialog.getText(dialog, 
            u'Get Editor Path',
            u'Path to external text editor:')
        path, ok = results
        if not ok:
            msg = 'Certain features will not work without '\
            'an external editor. \nYou can add or change '\
            'an external editor path later in Edit > Preferences.'
            msgBox = QtWidgets.QMessageBox()
            msgBox.setText(msg)
            msgBox.exec_()
            return None

    if path and os.path.isdir( os.path.dirname(path) ):
        editor_path = path
        os.environ['EXTERNAL_EDITOR_PATH'] = editor_path

        element = ElementTree.Element('external_editor_path')
        element.text = path
        root.append(element)

        header = '<?xml version="1.0" encoding="UTF-8"?>'
        data = ElementTree.tostring(root)
        with open(AUTOSAVE_FILE, 'w') as f:
            f.write(header+data)
            
    else:
        msg = u'External editor not found. '\
        'Certain features will not work.'\
        '\nYou can add or change an external '\
        'editor path later in Edit > Preferences.'
        msgBox = QtWidgets.QMessageBox()
        msgBox.setText(msg)
        msgBox.exec_()
        return None
