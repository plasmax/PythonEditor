import sys
import os

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
    SUBLIME_PATH = '/net/homes/mlast/software/sublime_text_3/sublime_text'
elif sys.platform == "darwin": # OS X
    raise NotImplementedError, 'Mac OS currently not supported.'
elif sys.platform == "win32": # Windows
    path = 'C:/Users'
    PATH_DELIM = ';'
    SUBLIME_PATH = 'C:/Program Files/Sublime Text 3/sublime_text.exe'

USER = os.environ.get('USERNAME')
NUKE_DIR = '/'.join([path, USER, '.nuke'])
AUTOSAVE_FILE = NUKE_DIR + '/PythonEditorHistory.xml'
QT_VERSION = pyside + PATH_DELIM + pyqt
os.environ['SUBLIME_PATH'] = SUBLIME_PATH
