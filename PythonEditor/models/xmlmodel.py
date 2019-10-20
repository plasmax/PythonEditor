import json

from PythonEditor.ui.Qt.QtCore import (
    Qt, QMimeData, Signal)
from PythonEditor.ui.Qt.QtGui import (
    QStandardItem, QStandardItemModel)
from PythonEditor.ui.features import autosavexml
from xml.etree import cElementTree as ElementTree


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
        mimeData = QMimeData()
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
