""" The TabView class is designed to represent
a one-dimensional array of data. It behaves like
a QListView and is meant to work in sync with other
views. The TabView class is data-agnostic. All methods
to do with the saving of data are implemented
on the model.
"""
from PythonEditor.ui.Qt.QtWidgets import QTabBar, QListView
from PythonEditor.ui.Qt.QtCore import Slot
from PythonEditor.ui.Qt.QtGui import QStandardItemModel, QStandardItem


def ismodel(model):
    """ Type check for QStandardItemModel. """
    return isinstance(model, QStandardItemModel)


class TabView(QTabBar):
    def __init__(self, parent=None):
        super(TabView, self).__init__(parent=parent)
        self.setTabsClosable(True)
        self.setMovable(True)

    def clear(self):
        for i in reversed(range(self.count())):
            self.tabBar.removeTab(i)

    def update_from_model(self):
        for i in range(self._model.rowCount()):
            item = self._model.item(i,0)
            text = item.text()
            self.addTab(text)

    _model = None
    def setModel(self, model):
        if not ismodel(model):
            raise TypeError(
                "setModel(model) argument must "
                "be a {!r}, not '{!r}'".format(
                 QStandardItemModel, type(model))
            )
        m = self.model()
        if m is not None:
            m.itemChanged.disconnect(
                self.tab_name_changed
            )

        self._model = model
        model.itemChanged.connect(
            self.tab_name_changed
        )
        self.tabMoved.connect(
            self.update_model_order
        )
        self.update_from_model()

    def model(self):
        return self._model

    _selection_model = None
    def selectionModel(self):
        return self._selection_model

    def setSelectionModel(self, model):
        self._selection_model = model

    model_moving = False
    @Slot(int, int)
    def update_model_order(self, _from, to):
        if self.model_moving:
            self.model_moving = False
            return
        m = self.model()
        m.insertRow(to, m.takeRow(_from))

    @Slot(QStandardItem)
    def tab_name_changed(self, item):
        index = item.index()
        # name column is 0
        if index.column() != 0:
            return
        self.setTabText(
            index.row(),
            item.text()
        )

    @Slot(int, int)
    def swap_tabs(self, _from, to):
        self.model_moving = True
        self.moveTab(_from, to)
        #from functools import partial
        #model_moved = partial(setattr, self, 'model_moving', False)
        #QTimer.singleShot(100, model_moved)


class ListView(QListView):
    def __init__(self):
        super(ListView, self).__init__()
        self.setDragDropMode(QListView.InternalMove)
        # self.setMovement(QListView.Snap)
        # self.setAcceptsDrops(True)

    @Slot(int, int)
    def row_moved(self, _from, to):
        self.setCurrentIndex(self.model().index(to, 0))

    def setModel(self, model):
        super(ListView, self).setModel(model)
        model.row_moved.connect(self.row_moved)

