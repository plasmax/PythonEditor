import sys
import os
dn = os.path.dirname
TESTS_DIR = dn(__file__)
PACKAGE_DIR = dn(TESTS_DIR)
folder = PACKAGE_DIR
sys.path.append(folder)

#from PythonEditor.ui import editor
from PythonEditor.ui import edittabs
from PythonEditor.ui import browser
from PythonEditor.ui.Qt import QtWidgets, QtGui, QtCore
reload(browser)


class Manager(QtWidgets.QWidget):
    def __init__(self):
        super(Manager, self).__init__()
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        left_widget = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_widget)

        path_edit = QtWidgets.QLineEdit()
        path_edit.__dict__.keys()
        path_edit.textChanged.connect(self.update_tree)
        self.path_edit = path_edit

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter = splitter

        self.setLayout(layout)
        self.tool_button = QtWidgets.QToolButton()
        self.tool_button.setText('<')
        self.tool_button.clicked.connect(self.xpand)
        self.tool_button.setMaximumWidth(20)

        self.xpanded = False
        layout.addWidget(splitter)

        nuke_folder = os.path.join(os.path.expanduser('~'), '.nuke')

        browse = browser.FileTree(nuke_folder)
        self.browser = browse
        left_layout.addWidget(self.path_edit)
        left_layout.addWidget(self.browser)

        #self.editor = editor.Editor()
        self.tabs = edittabs.EditTabs()
        self.tabs.new_tab()

        widgets = [left_widget,
                        self.tool_button,
                        self.tabs]
        for w in widgets:
            splitter.addWidget(w)

        splitter.setSizes([200,10, 800])

        # connect signals
        self.browser.path_signal.connect(self.set_file)

    def xpand(self):
        if self.xpanded:
            symbol = '<'
            sizes = [200, 10, 800]  # should be current sizes
        else:
            symbol = '>'
            sizes = [0, 10, 800]  # should be current sizes

        self.tool_button.setText(symbol)
        self.splitter.setSizes(sizes)
        self.xpanded = not self.xpanded

    @QtCore.Slot(str)
    def update_tree(self, path):
        model = self.browser.model()
        root_path = model.rootPath()
        if root_path in path:
            return
        path = os.path.dirname(path)
        if not os.path.isdir(path):
            return
        path = path+os.altsep
        print path
        self.browser.set_model(path)

    @QtCore.Slot(str)
    def set_file(self, path):
        # if no editor with path in tabs add new
        self.editor = self.tabs.currentWidget()
        if not os.path.isfile(path):
            return
        with open(path, 'rt') as f:
            self.editor.setPlainText(f.read())
            self.path_edit.setText(path)


m = Manager()
m.show()

QtWidgets.QFileSystemModel
