import sys
try:
    from PySide import QtGui, QtCore
except ImportError:
    sys.path.append('C:/Program Files/Nuke10.5v1/pythonextensions/site-packages')
    from PySide import QtGui, QtCore

class FileBrowser(QtGui.QDialog):
    pathSignal = QtCore.Signal(str)
    def __init__(self, path):
        QtGui.QDialog.__init__(self)

        # Build the user interface
        # =======================================
        self.setWindowTitle('Nuke Mini Browser')
        self._layout = QtGui.QVBoxLayout()
        self.setLayout(self._layout)
        self.resize(400, 320)

        self.model = QtGui.QFileSystemModel()
        self.model.setRootPath(path)

        self.fileTree = FileTree()#QtGui.QTreeView()
        self.fileTree.setModel(self.model)
        self.fileTree.header().setResizeMode(QtGui.QHeaderView.ResizeToContents) 
        self.fileTree.setRootIndex(self.model.index(path))
        self.fileTree.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        self._layout .addWidget(self.fileTree)

        # Signals
        # =======================================
        self.fileTree.clicked.connect(self.clickedAnItem)

    def clickedAnItem(self, item):
        print item, dir(item)
        index_sel = self.fileTree.selectedIndexes()[0]
        item = self.model.filePath(index_sel)
        print item, type(item)
        self.pathSignal.emit(item)

class FileTree(QtGui.QTreeView):
    def __init__(self):
        super(FileTree, self).__init__()
        
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            super(FileTree, self).mousePressEvent(event)

def make_panel(directory_path):
    global mini_browser
    mini_browser = FileBrowser(directory_path)
    mini_browser.show()
    
directory_path = 'C:/Users/Max-Last/.nuke' # replace with any path
    
if __name__ == '__main__':
    if not QtGui.QApplication.instance():
        app = QtGui.QApplication(sys.argv)
        make_panel(directory_path)
        sys.exit(app.exec_())
    else:
        make_panel(directory_path)



