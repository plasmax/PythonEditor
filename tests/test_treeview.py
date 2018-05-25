import sys
import os
dn = os.path.dirname
TESTS_DIR = dn(__file__)
PACKAGE_DIR = dn(TESTS_DIR)
folder = PACKAGE_DIR
sys.path.append(folder)

from PythonEditor.ui import manager
reload(manager)

m = manager.Manager()
m.show()
