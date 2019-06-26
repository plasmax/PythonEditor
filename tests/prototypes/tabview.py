from Qt import QtWidgets, QtGui, QtCore
from PythonEditor.ui.editor import Editor
from PythonEditor.ui.features import autosavexml
from xml.etree import cElementTree as ElementTree
import json
import os
import tempfile

from Qt.QtWidgets import *
from Qt.QtCore import *
from Qt.QtGui import *


class XMLModel(QStandardItemModel):
    def __init__(self):
        super(XMLModel, self).__init__()
        self.load_xml()
        self.itemChanged.connect(self.store_data)
        
    def load_xml(self):
        root, elements = autosavexml.parsexml('subscript')
        for element in elements:
            item1 = QStandardItem(element.attrib['name'])
            item2 = QStandardItem(element.text)
            item3 = QStandardItem(element.attrib['uuid'])
            self.appendRow([item1, item2, item3])

    def store_data(self, item):
        text = item.text()
        element = ElementTree.Element('subscript')
        element.text = text

    def flags(self, index):
        """
        https://www.qtcentre.org/threads/23258-How-to-reorder-items-in-QListView
        You still want the root index to accepts 
        drops, just not the items.
        This will work if the root index is 
        invalid (as it usually is). However, 
        if you use setRootIndex you may have 
        to compare against that index instead.
        """
        if index.isValid(): 
            return (
                Qt.ItemIsSelectable
                |Qt.ItemIsEditable
                |Qt.ItemIsDragEnabled
                |Qt.ItemIsEnabled
            )

        return (
            Qt.ItemIsSelectable
            |Qt.ItemIsDragEnabled
            |Qt.ItemIsDropEnabled
            |Qt.ItemIsEnabled
        )
        
    def mimeTypes(self):
        return ['text/json']

    def mimeData(self, indexes):
        data = {}
        row = indexes[0].row()
        data['name'] = self.item(row, 0).text()
        data['text'] = self.item(row, 1).text()
        data['uuid'] = self.item(row, 2).text()
        data['row'] = row            
        dragData = json.dumps(data, indent=2)
        mimeData = QtCore.QMimeData()
        mimeData.setData('text/json', dragData)
        return mimeData
    
    def stringList(self):
        """
        List of document names.
        """
        names = []
        for i in range(self.rowCount()):
            name = self.item(i,0).text()
            print name
            names.append(name)
        return names
            
    row_moved = Signal(int, int)
    def dropMimeData(self, data, action, row, column, parent=None):
        dropData = json.loads(bytes(data.data('text/json')))
        take_row = dropData['row']
        items = self.takeRow(take_row)
        if take_row < row:
            row -= 1
        elif row == -1:
            row = self.rowCount()
        print take_row, '->', row 
        self.insertRow(row, items)
        self.row_moved.emit(take_row, row)
        return True


class ListView(QListView):
    def __init__(self):
        super(ListView, self).__init__()
        self.setDragDropMode(QListView.InternalMove)
        
    @Slot(int, int)
    def row_moved(self, _from, to):
        self.setCurrentIndex(self.model().index(to, 0))
        
    def setModel(self, model):
        super(ListView, self).setModel(model)
        model.row_moved.connect(self.row_moved)
        
        
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
        if not isinstance(
                model, 
                QStandardItemModel
            ):
                raise TypeError(
                    "setModel(model) argument must be a {!r}, not '{!r}'".format(
                        QStandardItemModel, type(model)
                    )
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


class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.model = XMLModel()

        self.tabBar = TabView()
        #self.textEdit = QTextEdit()
        self.textEdit = Editor()
        #self.textEdit = QPlainTextEdit()
        #self.textEdit.setFont(QFont('DejaVu Sans'))
        self.listView = ListView()
        #self.treeView = QTreeView()
        #self.tableView = QTableView()
        self.nextButton = QPushButton("&Next")
        self.previousButton = QPushButton("&Previous")
        self.listButton = QToolButton()
        self.listButton.setArrowType(Qt.RightArrow)

        #b = QToolButton()
        self.listButton.setFixedSize(24, 24)
        self.mapper = QDataWidgetMapper(self)

        self.listView.setMaximumWidth(0)
        #self.listView.setAcceptsDrops(True)
        #self.listView.setMovement(QListView.Snap)

        self.textEdit.setMaximumHeight(1000)
        self.listView.setModel(self.model)
        
        #self.treeView.setModel(self.model)
        #self.tableView.setModel(self.model)
        
        self.tabBar.setModel(self.model)

        self.mapper.setModel(self.model)
        self.mapper.addMapping(self.textEdit, 1)

        self.selection_model = self.listView.selectionModel()
        self.selection_model.currentRowChanged.connect(self.mapper.setCurrentModelIndex)
        self.tabBar.currentChanged.connect(self.mapper.setCurrentIndex)
        self.tabBar.setSelectionModel(self.selection_model)
        self.textEdit.modificationChanged.connect(self.submit_and_refocus)
        self.mapper.currentIndexChanged.connect(self.tabBar.setCurrentIndex)
        self.mapper.currentIndexChanged.connect(self.setListIndex)
        #self.addressEdit.textChanged.connect(self.mapper.submit)
        self.nextButton.clicked.connect(self.mapper.toNext)
        self.previousButton.clicked.connect(self.mapper.toPrevious)
        self.mapper.currentIndexChanged.connect(self.updateButtons)
        self.model.row_moved.connect(self.tabBar.swap_tabs)
        #self.model.row_moved.connect(self.tabBar.moveTab)
        
        self.listButton.clicked.connect(self.animate_listview)

        layout = QGridLayout(self)
        layout.addWidget(self.listButton, 0, 0)
        layout.addWidget(self.listView, 1, 0)
        layout.addWidget(self.tabBar, 0, 1, 1, 1, Qt.AlignTop)
        layout.addWidget(self.textEdit, 1, 1, 1, 1)#, Qt.AlignTop)
        #layout.addWidget(self.treeView, 1, 2)
        #layout.addWidget(self.tableView, 1, 3)
        #layout.addWidget(self.nextButton, 0, 1, 1, 1)
        #layout.addWidget(self.previousButton, 1, 1, 1, 1)
        self.setLayout(layout)

        self.setWindowTitle("Simple Widget Mapper")
        self.mapper.toFirst()
        #QTimer.singleShot(1000, self.animate_listview)
        
    def animate_listview(self, start=0, end=300):
        if self.listView.maximumWidth() != 0:
            start, end = end, start
            self.listButton.setArrowType(Qt.RightArrow)
        else:
            self.listButton.setArrowType(Qt.DownArrow)
        anim = QtCore.QPropertyAnimation(
            self.listView,
            'maximumWidth'
        )
        self._anim = anim
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setDuration(300)
        anim.start()
        
    @Slot()
    def submit_and_refocus(self):
        cursor = self.textEdit.textCursor()
        self.mapper.submit()
        self.textEdit.setTextCursor(cursor)
                
    @Slot(int)
    def setListIndex(self, row):
        index = self.model.index(row, 0)
        self.listView.setCurrentIndex(index)
            
    @Slot(int)
    def updateButtons(self, row):
        self.previousButton.setEnabled(row > 0)
        self.nextButton.setEnabled(row < self.model.rowCount()-1)


if __name__ == '__main__':
    w = Window()
    w.show()