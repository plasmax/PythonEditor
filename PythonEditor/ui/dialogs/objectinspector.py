import os
from __main__ import __dict__

if not os.environ.get('QT_PREFERRED_BINDING'):
    os.environ['QT_PREFERRED_BINDING'] = 'PySide'

from PythonEditor.ui.Qt import QtWidgets, QtCore, QtGui


class ObjectInspector(QtWidgets.QWidget):
    """
    Inspired by the Object Inspector from
    the Pythonista app.
    """
    def __init__(self):
        super(ObjectInspector, self).__init__()
        self.layout = QtWidgets.QGridLayout(self)

        self.setMinimumWidth(900)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.treeview = QtWidgets.QTreeView()
        self.treemodel = QtGui.QStandardItemModel()
        self.treeview.setModel(self.treemodel)
        self.treeview.setUniformRowHeights(True)

        self.layout.addWidget(self.treeview)

        self.treemodel.setHorizontalHeaderLabels(['object name',
                                                 'object'])

        self.treeview.header().setStretchLastSection(False)
        mode = QtWidgets.QHeaderView.ResizeToContents
        self.treeview.header().setResizeMode(mode)

        self.load_globals()
        self.start_timer()

    def load_globals(self):
        """
        Load globals into Tree
        """
        self.treemodel.removeRows(0, self.treemodel.rowCount())

        self.names = __dict__.copy()

        rootItem = self.treemodel.invisibleRootItem()
        for key, value in __dict__.iteritems():
            # if hasattr(value, '__repr__'):
            try:
                items = [QtGui.QStandardItem(i.__repr__())
                         for i in [key, value]]
                rootItem.appendRow(items)
            except Exception as e:
                print(key, value, e)

    def start_timer(self):
        """
        Starts timer for
        self.check_update_globals
        """
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.check_update_globals)
        self.timer.start()

    def check_update_globals(self):
        """
        Timer that checks len() of
        __main__.__dict__
        and updates globals on new items.
        """
        if not self.names == __dict__:
            self.load_globals()

    def open_in_external_editor(self):
        """
        Like sublime's "Go to"
        Open file in which object was defined.
        TODO: Would be excellent to jump to line.
        """
        pass
