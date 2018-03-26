""" For testing independently. """
import sys
import os

TESTS_DIR = os.path.dirname(__file__)
PACKAGE_PATH = os.path.dirname( TESTS_DIR )
sys.path.append( PACKAGE_PATH )

for m in sys.modules.keys():
    if 'codeeditor' in m:
        del sys.modules[m]

import codeeditor
reload(codeeditor)

if __name__ == '__main__':
    from codeeditor.ui.Qt import QtWidgets, QtGui, QtCore
    app = QtWidgets.QApplication(sys.argv)
    ide = codeeditor.ide.IDE()
    ide.show()
    ide.resize(500, 800)
    QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Plastique'))
    sys.exit(app.exec_())
