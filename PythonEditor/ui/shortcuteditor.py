from PythonEditor.ui.Qt import QtWidgets, QtCore, QtGui

class ShortcutEditor(QtWidgets.QTreeView):
    """
    A display widget that allows editing of
    keyboard shortcuts assigned to the editor.
    TODO: Make this editable, and reassign shortcuts on edit.
    """
    def __init__(self, shortcuthandler):
        super(ShortcutEditor, self).__init__()
        self.shortcuthandler = shortcuthandler
        self.shortcut_dict = shortcuthandler.shortcut_dict        

        model = QtGui.QStandardItemModel()
        self.setModel(model)
        root = model.invisibleRootItem()
        model.setHorizontalHeaderLabels(['Shortcut', 'Description'])

        for item in self.shortcut_dict.items():
            row = [QtGui.QStandardItem(val) for val in item]
            model.appendRow(row)

        self.header().setStretchLastSection(False)
        self.header().setResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setUniformRowHeights(True)
        self.resize(500, 400)
