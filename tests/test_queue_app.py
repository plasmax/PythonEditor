""" For testing independently. """
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

test_queue = os.path.join(TESTS_DIR, 'test_queue.py')
with open(test_queue, 'r') as f:
    test_code = f.read()

if __name__ == '__main__':
    """
    For testing outside of nuke.
    """
    from PythonEditor.ui.Qt import QtWidgets
    from PythonEditor.ui.features import nukepalette

    app = QtWidgets.QApplication(sys.argv)
    ide = PythonEditor.ui.editor.Editor()
    app.setPalette(nukepalette.getNukePalette())
    ide.show()
    ide.setPlainText(test_code)
    ide.resize(500, 800)
    plastique = QtWidgets.QStyleFactory.create('Plastique')
    QtWidgets.QApplication.setStyle(plastique)
    sys.exit(app.exec_())
