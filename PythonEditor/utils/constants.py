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

if sys.platform == "linux" or sys.platform == "linux2":
    # linux
    path = '/net/homes'
    PATH_DELIM = ':'
elif sys.platform == "darwin": # OS X
    raise NotImplementedError, 'Mac OS currently not supported.'
elif sys.platform == "win32": # Windows
    path = 'C:/Users'
    PATH_DELIM = ';'

USER = os.environ.get('USERNAME')
NUKE_DIR = '/'.join([path, USER, '.nuke'])
AUTOSAVE_FILE = NUKE_DIR + '/PythonEditorHistory.xml'
QT_VERSION = pyside + PATH_DELIM + pyqt

def get_external_editor_path():
    """
    Checks the autosave file for a <external_editor_path> element.
    Prompts the user for it if it doesn't exist.
    """
    parser = ElementTree.parse(AUTOSAVE_FILE)
    root = parser.getroot()
    editor_elements = root.findall('external_editor_path')

    editor_path = None
    if editor_elements:
        editor_element = editor_elements[0] 
        if os.path.isdir( os.path.dirname(editor_element.text) ):
            editor_path = editor_element.text

    if not editor_path:
        from PythonEditor.ui.Qt import QtWidgets
        dialog = QtWidgets.QInputDialog()
        results = QtWidgets.QInputDialog.getText(dialog, 
            u'Get Editor Path',
            u'Path to external text editor:')
        text, ok = results

        if text and os.path.isdir( os.path.dirname(text) ):
            editor_path = text

            element = ElementTree.Element('external_editor_path')
            element.text = text
            root.append(element)

            header = '<?xml version="1.0" encoding="UTF-8"?>'
            data = ElementTree.tostring(root)
            with open(AUTOSAVE_FILE, 'w') as f:
                f.write(header+data)
        else:
            msg = u'External editor not found. '\
            'Certain features will not work.'\
            '\nYou can add or change an external '\
            'editor path later in Edit>Preferences.'
            msgBox = QtWidgets.QMessageBox()
            msgBox.setText(msg)
            msgBox.exec_()
            return None

    os.environ['EXTERNAL_EDITOR_PATH'] = editor_path # TODO: should be generic environment variable
    return editor_path
