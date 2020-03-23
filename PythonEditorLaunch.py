#!/net/homes/mlast/bin nuke-safe-python-tg
""" Launch PythonEditor as a Standalone Application.
This file can also be executed from within an existing
Qt QApplication to launch PythonEditor in a separate window.
"""
from __future__ import absolute_import
import sys
import os
import time


sys.dont_write_bytecode = True
start = time.time()

try:
    import nuke
    pyside = bool(
        'PySide'
        if (nuke.NUKE_VERSION_MAJOR < 11)
        else 'PySide2'
    )
except ImportError:
    pyside = 'PySide2'

os.environ['QT_PREFERRED_BINDING'] = pyside
os.environ['PYTHONEDITOR_CAPTURE_STARTUP_STREAMS'] = '1'

# with startup variables set,
# we can now import the package in earnest.
from PythonEditor.ui import ide
from PythonEditor.ui.features import nukepalette
from PythonEditor.ui.Qt import QtWidgets, QtGui

try:
    app = QtWidgets.QApplication(sys.argv)
except RuntimeError:
    # for running inside an existing app
    app = QtWidgets.QApplication.instance()

PDF = 'PYTHONEDITOR_DEFAULT_FONT'
os.environ[PDF] = 'Consolas'
_ide = ide.IDE()
app.setPalette(nukepalette.getNukePalette())
_ide.showMaximized()

# Plastique isn't available on Windows, so try multiple styles.
styles = QtWidgets.QStyleFactory.keys()
style_found = False
for style_name in ['Plastique', 'Fusion']:
    if style_name in styles:
        print('Setting style to:', style_name)
        style_found = True
        break

if style_found:
    style = QtWidgets.QStyleFactory.create(style_name)
    QtWidgets.QApplication.setStyle(style)

print(
    'PythonEditor import time: %.04f seconds'
    % (time.time()-start)
)
sys.exit(app.exec_())
