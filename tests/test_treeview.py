import sys
import os
dn = os.path.dirname
folder = dn(dn(__file__))
sys.path.append(folder)

from PythonEditor.ui import editor
from PythonEditor.ui import browser
from PythonEditor.ui.Qt import QtWidgets, QtGui, QtCore
reload(browser)


class Manager(QtWidgets.QWidget):
    def __init__(self):
        super(Manager, self).__init__()
        layout = QtWidgets.QHBoxLayout(self)
        t = browser.FileTree(folder)
        t.path_signal.connect(self.set_file)

        e = editor.Editor()
        self.e = e
        for x in t, e:
            layout.addWidget(x)

    @QtCore.Slot(str)
    def set_file(self, path):
        if not os.path.isfile(path):
            return
        with open(path, 'rt') as f:
            self.e.setPlainText(f.read())


m = Manager()
m.show()
