""" For testing independently. """
import sys
import os

TESTS_DIR = os.path.dirname(__file__)
PACKAGE_PATH = os.path.dirname( TESTS_DIR )
sys.path.append( PACKAGE_PATH )

for m in sys.modules.keys():
    if 'PythonEditor' in m:
        del sys.modules[m]

import PythonEditor
reload(PythonEditor)

if __name__ == '__main__':
    from PythonEditor.ui.Qt import QtWidgets, QtGui, QtCore
    app = QtWidgets.QApplication(sys.argv)
    ide = PythonEditor.ide.IDE()
    ide.show()
    ide.resize(500, 800)
    QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Plastique'))
    sys.exit(app.exec_())
