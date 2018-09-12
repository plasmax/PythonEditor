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
QT_VERSION = os.pathsep.join([pyside, pyqt])

DEFAULT_FONT = 'Courier New' if (os.name == 'nt') else 'DejaVu Sans Mono'



