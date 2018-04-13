import sys
import os

from PythonEditor.ui.Qt import QtGui, QtCore, QtWidgets
from PythonEditor.utils.constants import NUKE_DIR

class FileBrowser(QtWidgets.QDialog):
    pathSignal = QtCore.Signal(str)
    def __init__(self, path):
        QtWidgets.QDialog.__init__(self)

        # Build the user interface
        # =======================================
        self.setWindowTitle('Nuke Mini Browser')
        self._layout = QtWidgets.QVBoxLayout()
        self.setLayout(self._layout)
        self.resize(400, 320)

        self.model = QtWidgets.QFileSystemModel()
        self.model.setRootPath(path)

        self.fileTree = FileTree()#QtWidgets.QTreeView()
        self.fileTree.setModel(self.model)
        self.fileTree.header().setResizeMode(QtWidgets.QHeaderView.ResizeToContents) 
        self.fileTree.setRootIndex(self.model.index(path))
        self.fileTree.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self._layout.addWidget(self.fileTree)

        # Signals
        # =======================================
        self.fileTree.clicked.connect(self.clickedAnItem)

    def clickedAnItem(self, item):
        # print item, dir(item)
        index_sel = self.fileTree.selectedIndexes()[0]
        item = self.model.filePath(index_sel)
        print item, type(item)
        self.pathSignal.emit(item)

class FileTree(QtWidgets.QTreeView):
    def __init__(self):
        super(FileTree, self).__init__()
        
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            super(FileTree, self).mousePressEvent(event)

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



