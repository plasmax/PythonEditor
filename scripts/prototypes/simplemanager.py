import os
import sys


def cd_up(path, level=1):
    for d in range(level):
        path = os.path.dirname(path)
    return path


package_dir = cd_up(__file__, level=3)
sys.path.insert(0, package_dir)

from PythonEditor.ui.Qt import QtWidgets, QtCore
from PythonEditor.ui import editor
from PythonEditor.ui import browser
from PythonEditor.ui import menubar
from PythonEditor.utils.constants import NUKE_DIR


def get_parent(widget, level=1):
    """
    Return a widget's nth parent widget.
    """
    parent = widget
    for p in range(level):
        parent = parent.parentWidget()
    return parent


class Manager(QtWidgets.QWidget):
    """
    Manager with only one file connected at a time.
    """
    def __init__(self):
        super(Manager, self).__init__()
        self.currently_viewed_file = None
        self.build_layout()

    def build_layout(self):
        """
        Create the layout.
        """
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        # self.setup_menu()
        self.read_only = True
        self.menubar = menubar.MenuBar(self)

        left_widget = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_widget)

        path_edit = QtWidgets.QLineEdit()
        path_edit.textChanged.connect(self.update_tree)
        self.path_edit = path_edit

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter = splitter

        self.xpanded = False
        self.setLayout(layout)
        self.tool_button = QtWidgets.QToolButton()
        self.tool_button.setText('<')
        self.tool_button.clicked.connect(self.xpand)
        self.tool_button.setMaximumWidth(20)

        layout.addWidget(splitter)

        browse = browser.FileTree(NUKE_DIR)
        self.browser = browse
        left_layout.addWidget(self.path_edit)
        left_layout.addWidget(self.browser)

        self.editor = editor.Editor(handle_shortcuts=True)
        self.editor.path = 'C:/Users/tsalx/Desktop/temp_editor_save.py'

        widgets = [left_widget,
                   self.tool_button,
                   self.editor]
        for w in widgets:
            splitter.addWidget(w)

        splitter.setSizes([200, 10, 800])
        self.browser.path_signal.connect(self.read)
        self.editor.textChanged.connect(self.write)
        self.editor.modificationChanged.connect(self.handle_changed)

    def xpand(self):
        """
        Expand or contract the QSplitter
        to show or hide the file browser.
        """
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
        """
        Update the file browser when the
        lineedit is updated.
        """
        model = self.browser.model()
        root_path = model.rootPath()
        if root_path in path:
            return
        path = os.path.dirname(path)
        if not os.path.isdir(path):
            return
        path = path+os.altsep
        print(path)
        self.browser.set_model(path)

    @QtCore.Slot(str)
    def read(self, path):
        """
        Read from text file.
        """
        self.read_only = True
        self.path_edit.setText(path)
        if not os.path.isfile(path):
            return

        with open(path, 'rt') as f:
            text = f.read()
            self.editor.setPlainText(text)

        self.editor.path = path

    @QtCore.Slot()
    def write(self):
        """
        Write to text file.
        """
        if self.read_only:
            return

        path = self.editor.path

        with open(path, 'wt') as f:
            f.write(self.editor.toPlainText())

    def handle_changed(self, changed):
        self.read_only = not changed

    def showEvent(self, event):
        """
        Hack to get rid of margins automatically put in
        place by Nuke Dock Window.
        """
        try:
            for i in 2, 4:
                parent = get_parent(self, level=i)
                parent.layout().setContentsMargins(0, 0, 0, 0)
        except Exception:
            pass

        super(Manager, self).showEvent(event)


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    m = Manager()
    m.show()
    app.exec_()
