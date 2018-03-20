import sys
import os

TESTS_DIR = os.path.dirname(__file__)
PACKAGE_PATH = os.path.dirname( TESTS_DIR )
sys.path.append( PACKAGE_PATH )
TEST_FILE = os.path.join( PACKAGE_PATH, 'tests/test_code.py')

with open( TEST_FILE, 'r' ) as f:
    TEST_CODE = f.read()

for m in sys.modules.keys():
    if 'codeeditor' in m:
        del sys.modules[m]

import codeeditor
reload(codeeditor)

"""
#For testing within nuke:
PACKAGE_PATH = '/net/homes/mlast/.nuke/python/max/tests/CodeEditor'
TEST_FILE = os.path.join( PACKAGE_PATH, 'tests/test_code.py')

with open( TEST_FILE, 'r' ) as f:
    TEST_CODE = f.read()

sys.path.append(PACKAGE_PATH)

for m in sys.modules.keys():
    if 'codeeditor' in m:
        del sys.modules[m]

import codeeditor
reload(codeeditor)
ide = codeeditor.ide.IDE()
ide.show()
ide.editor.setPlainText(TEST_CODE)

import nukescripts
nukescripts.registerWidgetAsPanel('__import__("codeeditor").ide.IDE', 
                                  'Python Editor', 'i.d.e')

"""

def main():
    """
    For testing outside of nuke.
    """
    from codeeditor.ui.Qt import QtWidgets, QtGui
    app = QtWidgets.QApplication(sys.argv)
    ide = codeeditor.ide.IDE()
    ide.show()
    ide.editor.setPlainText(TEST_CODE)
    QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Plastique'))
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
