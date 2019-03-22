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

NUKE_DIR = os.path.join(
	os.path.expanduser('~'),
	'.nuke'
)
PYTHONEDITOR_CUSTOM_DIR = os.getenv(
	'PYTHONEDITOR_CUSTOM_DIR'
)
if PYTHONEDITOR_CUSTOM_DIR is not None:
	if os.path.isdir(PYTHONEDITOR_CUSTOM_DIR):
		NUKE_DIR = PYTHONEDITOR_CUSTOM_DIR

QT_VERSION = os.pathsep.join([pyside, pyqt])

DEFAULT_FONT = (
    'Courier New'
    if (os.name == 'nt')
    else 'DejaVu Sans Mono'
)
os.environ[
	'PYTHONEDITOR_DEFAULT_FONT'
] = DEFAULT_FONT
