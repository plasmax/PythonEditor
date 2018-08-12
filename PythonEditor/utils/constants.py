import os
from xml.etree import ElementTree

pyside = 'PySide'
pyqt = 'PyQt4'

IN_NUKE = 'nuke' in globals()
if IN_NUKE:
    import nuke
    if nuke.NUKE_VERSION_MAJOR > 10:
        pyside = 'PySide2'
        pyqt = 'PyQt5'

USER = os.environ.get('USERNAME')
NUKE_DIR = os.path.join(os.path.expanduser('~'), '.nuke')
AUTOSAVE_FILE = os.path.join(NUKE_DIR, 'PythonEditorHistory.xml')
QT_VERSION = os.pathsep.join([pyside, pyqt])

XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>'
DEFAULT_FONT = 'Courier New' if (os.name == 'nt') else 'DejaVu Sans Mono'

def create_autosave_file():
    if not os.path.isfile(AUTOSAVE_FILE):
        if not os.path.isdir(os.path.dirname(AUTOSAVE_FILE)):
            return False
        else:
            with open(AUTOSAVE_FILE, 'w') as f:
                f.write(XML_HEADER+'<script></script>')
    return True


def get_editor_xml():
    if not create_autosave_file():
        return
    parser = ElementTree.parse(AUTOSAVE_FILE)
    root = parser.getroot()
    editor_elements = root.findall('external_editor_path')
    return root, editor_elements


def get_external_editor_path():
    """
    Checks the autosave file for an
    <external_editor_path> element.
    """
    editor_path = os.environ.get('EXTERNAL_EDITOR_PATH')
    if (editor_path is not None
            and os.path.isdir(os.path.dirname(editor_path))):
        return editor_path

    root, editor_elements = get_editor_xml()

    if editor_elements:
        editor_element = editor_elements[0]
        path = editor_element.text
        if path and os.path.isdir(os.path.dirname(path)):
            editor_path = path

    if editor_path:
        os.environ['EXTERNAL_EDITOR_PATH'] = editor_path
        return editor_path
    else:
        return set_external_editor_path(ask_user=True)


def set_external_editor_path(path=None, ask_user=False):
    """
    Prompts the user for a new
    external editor path.
    TODO: Set temp program if none found.
    """
    root, editor_elements = get_editor_xml()
    for e in editor_elements:
        root.remove(e)

    if ask_user and not path:
        from PythonEditor.ui.Qt import QtWidgets
        dialog = QtWidgets.QInputDialog()
        args = (dialog,
                u'Get Editor Path',
                u'Path to external text editor:')
        results = QtWidgets.QInputDialog.getText(*args)
        path, ok = results
        if not ok:
            msg = 'Certain features will not work without '\
                'an external editor. \nYou can add or change '\
                'an external editor path later in Edit > Preferences.'
            msgBox = QtWidgets.QMessageBox()
            msgBox.setText(msg)
            msgBox.exec_()
            return None

    if path and os.path.isdir(os.path.dirname(path)):
        editor_path = path
        os.environ['EXTERNAL_EDITOR_PATH'] = editor_path

        element = ElementTree.Element('external_editor_path')
        element.text = path
        root.append(element)

        header = '<?xml version="1.0" encoding="UTF-8"?>'
        data = ElementTree.tostring(root)
        with open(AUTOSAVE_FILE, 'w') as f:
            f.write(header+data)
        return path

    elif ask_user:
        from PythonEditor.ui.Qt import QtWidgets
        msg = u'External editor not found. '\
              'Certain features will not work.'\
              '\nYou can add or change an external '\
              'editor path later in Edit > Preferences.'
        msgBox = QtWidgets.QMessageBox()
        msgBox.setText(msg)
        msgBox.exec_()
        return None
