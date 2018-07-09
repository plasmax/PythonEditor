import sys
import os
dn = os.path.dirname
TESTS_DIR = dn(__file__)
PACKAGE_DIR = dn(TESTS_DIR)
folder = PACKAGE_DIR
sys.path.append(folder)

from PythonEditor.ui import manager
from PythonEditor.ui.Qt import QtWidgets


if __name__ == '__main__':
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
        m = manager.Manager()
        m.show()
        sys.exit(app.exec_())
    else:
        m = manager.Manager()
        m.show()
