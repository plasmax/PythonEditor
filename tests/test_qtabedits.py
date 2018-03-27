import sys
import os

TESTS_DIR = os.path.dirname(__file__)
PACKAGE_PATH = os.path.dirname( TESTS_DIR )
sys.path.append( PACKAGE_PATH )
TEST_FILE = os.path.join( PACKAGE_PATH, 'tests/test_code.py')

with open( TEST_FILE, 'r' ) as f:
    TEST_CODE = f.read()

for m in sys.modules.keys():
    if 'PythonEditor' in m:
        del sys.modules[m]

from PythonEditor.ui.Qt import QtWidgets, QtGui, QtCore
from PythonEditor.ui import idetabs 

@QtCore.Slot(int)
def cw(num):
    print num

if __name__ == '__main__':
    """
    For testing outside of nuke.
    """
    app = QtWidgets.QApplication(sys.argv)
    ide = idetabs.IDE()
    ide.show()
    QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Plastique'))
    sys.exit(app.exec_())
