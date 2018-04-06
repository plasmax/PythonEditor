import sys
import os

sys.dont_write_bytecode = True
TESTS_DIR = os.path.dirname(__file__)
PACKAGE_PATH = os.path.dirname( TESTS_DIR )
sys.path.append( PACKAGE_PATH )

for m in sys.modules.keys():
    if 'PythonEditor' in m:
        del sys.modules[m]


import PythonEditor
reload(PythonEditor)

if __name__ == '__main__':
    """
    For testing outside of nuke.
    """
    from PythonEditor.ui.Qt import QtWidgets, QtGui, QtCore
    from PythonEditor.ui.features import nukepalette

    app = QtWidgets.QApplication(sys.argv)
    ide = PythonEditor.ide.IDE(tabs=True)
    app.setPalette(nukepalette.getNukePalette())
    ide.show()
    QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Plastique'))
    sys.exit(app.exec_())