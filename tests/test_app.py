#!/usr/bin/env nuke-python
""" For testing independently. """
from __future__ import absolute_import
import sys
import os
import imp

sys.dont_write_bytecode = True
TESTS_DIR = os.path.dirname(__file__)
PACKAGE_PATH = os.path.dirname(TESTS_DIR)
sys.path.append(PACKAGE_PATH)

for m in sys.modules.keys():
    if 'PythonEditor' in m:
        del sys.modules[m]

import PythonEditor
imp.reload(PythonEditor)

if __name__ == '__main__':
    """
    For testing outside of nuke.
    """
    from PythonEditor.ui.Qt import QtWidgets
    from PythonEditor.ui.features import nukepalette

    app = QtWidgets.QApplication(sys.argv)
    ide = PythonEditor.ide.IDE()
    app.setPalette(nukepalette.getNukePalette())
    ide.show()
    ide.setStyleSheet('font-family:Consolas;font-size:8pt;')
    ide.resize(500, 800)
    plastique = QtWidgets.QStyleFactory.create('Plastique')
    QtWidgets.QApplication.setStyle(plastique)
    sys.exit(app.exec_())
