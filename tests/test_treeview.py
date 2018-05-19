import sys
import os
dn = os.path.dirname
TESTS_DIR = dn(__file__)
PACKAGE_DIR = dn(TESTS_DIR)
folder = PACKAGE_DIR
sys.path.append(folder)

from PythonEditor.ui import editor
from PythonEditor.ui import browser
from PythonEditor.ui.Qt import QtWidgets, QtGui, QtCore
reload(browser)


class Manager(QtWidgets.QWidget):
    def __init__(self):
        super(Manager, self).__init__()
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)

        left_widget = QtWidgets.QWidget()
        left_layout = QtWidgets.QHBoxLayout(left_widget)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter = splitter

        self.setLayout(layout)
        b = QtWidgets.QToolButton()
        b.setText('>')
        b.clicked.connect(self.xpand)
        b.setMaximumWidth(20)
        self.b = b
        self.xpanded = False
        layout.addWidget(splitter)
        #layout.setWidgetResizable(True)

        nuke_folder = os.path.join(os.path.expanduser('~'), '.nuke')
        t = browser.FileTree(nuke_folder)
        t.path_signal.connect(self.set_file)

        e = editor.Editor()
        self.e = e
        #for x in t, e:
        for x in t, b, e:
            splitter.addWidget(x)
        #splitter.setStretchFactor(1, 2)
        splitter.setSizes([200,10, 800])
        #splitter.setStretchFactor(2, 2)
    def xpand(self):
        if self.xpanded:
            symbol = '>'
            sizes = [200, 10, 800]  # should be current sizes
        else:
            symbol = '<'
            sizes = [0, 10, 800]  # should be current sizes

        self.b.setText(symbol)
        self.splitter.setSizes(sizes)
        self.xpanded = not self.xpanded


    @QtCore.Slot(str)
    def set_file(self, path):
        if not os.path.isfile(path):
            return
        with open(path, 'rt') as f:
            self.e.setPlainText(f.read())



# m = Manager()
# m.show()
