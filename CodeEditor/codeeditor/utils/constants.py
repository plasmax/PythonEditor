"""
TODO: Update to latest version.
"""
import sys
import os

try:
    import nuke
    if nuke.NUKE_VERSION_MAJOR > 10:
        pyside = 'PySide2'
        pyqt = 'PyQt5'
    else:
        raise NotImplementedError
except Exception:
    pyside = 'PySide'
    pyqt = 'PyQt4'

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
