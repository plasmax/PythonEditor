#!/net/homes/mlast/Desktop nuke-tg-python
""" For testing independently. """
from __future__ import absolute_import
import sys
import os
import imp

sys.dont_write_bytecode = True
TESTS_DIR = os.path.dirname(__file__)
PACKAGE_PATH = os.path.dirname(TESTS_DIR)
sys.path.append(PACKAGE_PATH)

if __name__ == '__main__':
    """
    For testing outside of nuke.
    """
    os.environ['QT_PREFERRED_BINDING'] = 'PySide2:PyQt5:PySide:PyQt4'

    from PythonEditor.ui.features import nukepalette
    from PythonEditor.ui import ide
    from PythonEditor.ui.Qt import QtWidgets

    try:
        app = QtWidgets.QApplication(sys.argv)
    except RuntimeError:
        # for running inside and outside of Nuke
        app = QtWidgets.QApplication.instance()

    ide = ide.IDE()
    app.setPalette(nukepalette.getNukePalette())
    ide.show()
    ide.resize(500, 800)
    plastique = QtWidgets.QStyleFactory.create('Plastique')
    QtWidgets.QApplication.setStyle(plastique)
    sys.exit(app.exec_())
