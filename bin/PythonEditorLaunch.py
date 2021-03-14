#!/net/homes/mlast/bin nuke-safe-python-tg
""" Launch PythonEditor as a Standalone Application.
This file can also be executed from within an existing
Qt QApplication to launch PythonEditor in a separate window.
"""
from __future__ import absolute_import
import time
start = time.time()

import os
import sys
import signal
try:
    import PySide2
    pyside = 'PySide2'
except ImportError:
    pyside = 'PySide'


# Python's default signal handler doesn't work nicely with Qt, meaning
# that ctrl-c won't work. Bypass Python's signal handling.
signal.signal(signal.SIGINT, signal.SIG_DFL)

# do not create .pyc files
sys.dont_write_bytecode = True

# add the package path to sys.path
FOLDER = os.path.dirname(__file__)
PACKAGE_PATH = os.path.dirname(FOLDER)
if PACKAGE_PATH not in sys.path:
    sys.path.append(PACKAGE_PATH)

# set startup env variables
os.environ['QT_PREFERRED_BINDING'] = pyside
try:
	# allow this variable to be set before launching
	os.environ['PYTHONEDITOR_CAPTURE_STARTUP_STREAMS']
except KeyError:
	print('Will try and encapsulate sys.stdout immediately.')
	os.environ['PYTHONEDITOR_CAPTURE_STARTUP_STREAMS'] = '1'
os.environ['PYTHONEDITOR_DEFAULT_FONT'] = 'Consolas'

from PythonEditor.ui import ide
from PythonEditor.ui.features import nukepalette
from PythonEditor.ui.Qt import QtWidgets, QtGui

try:
    app = QtWidgets.QApplication(sys.argv)
except RuntimeError:
    # for running inside and outside of other applications
    app = QtWidgets.QApplication.instance()

# set the application icon
ICON_PATH = os.path.join(PACKAGE_PATH, 'icons', 'PythonEditor.png')
icon = QtGui.QIcon(ICON_PATH)
app.setWindowIcon(icon)

# set style (makes palette work on linux)
# Plastique isn't available on Windows, so try multiple styles.
styles = QtWidgets.QStyleFactory.keys()
for style_name in ['Plastique', 'Fusion']:
    if style_name not in styles:
        continue
    print('Setting style to:', style_name)
    style = QtWidgets.QStyleFactory.create(style_name)
    QtWidgets.QApplication.setStyle(style)
    break

app.setPalette(nukepalette.getNukePalette())

_ide = ide.IDE()
_ide.showMaximized()

print('PythonEditor startup time: %.04f seconds'%(time.time()-start))

# run
sys.exit(app.exec_())
