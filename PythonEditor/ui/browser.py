import sys

from PythonEditor.ui.Qt import QtCore, QtWidgets, QtGui
from PythonEditor.utils.constants import NUKE_DIR


class FileTree(QtWidgets.QTreeView):
    path_signal = QtCore.Signal(str)

    def __init__(self, path):
        super(FileTree, self).__init__()
        self.set_model(path)

    def set_model(self, path):
        model = QtWidgets.QFileSystemModel()
        model.setRootPath(path)
        model.setNameFilterDisables(False)
        model.setNameFilters(['*.py',
                              '*.txt',
                              '*.md'])

        self.setModel(model)
        RTC = QtWidgets.QHeaderView.ResizeToContents
        self.header().setResizeMode(RTC)
        self.setRootIndex(model.index(path))

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            super(FileTree, self).mousePressEvent(event)
        if event.button() == QtCore.Qt.RightButton:
            menu = QtWidgets.QMenu()
            menu.addAction('New File', 'print "does nothing"')
            cursor = QtGui.QCursor()
            pos = cursor.pos()
            menu.exec_(pos)

    def selectionChanged(self, selected, deselected):
        index_sel = selected.indexes()[0]
        item = self.model().filePath(index_sel)
        self.path_signal.emit(item)


class FileBrowser(QtWidgets.QDialog):
    def __init__(self, path):
        QtWidgets.QDialog.__init__(self)

        self.setWindowTitle('Nuke Mini Browser')
        self._layout = QtWidgets.QVBoxLayout()
        self.setLayout(self._layout)
        self.resize(400, 320)

        self.file_tree = FileTree(path)
        self._layout.addWidget(self.file_tree)


def make_panel(directory_path):
    global mini_browser
    mini_browser = FileBrowser(directory_path)
    mini_browser.show()


if __name__ == '__main__':
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
        make_panel(NUKE_DIR)
        sys.exit(app.exec_())
    else:
        make_panel(NUKE_DIR)
