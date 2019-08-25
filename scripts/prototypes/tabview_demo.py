
from PythonEditor.ui.Qt.QtCore import QPropertyAnimation, Qt, Slot, QTimer
from PythonEditor.ui.Qt.QtGui import QStandardItem
from PythonEditor.ui.Qt.QtWidgets import (
    QDataWidgetMapper, QWidget, QPushButton, QToolButton, QGridLayout)

from PythonEditor.ui.editor import Editor
from PythonEditor.ui.tabview import TabView, ListView
from PythonEditor.models.xmlmodel import XMLModel


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
        # self.nextButton = QPushButton("&Next")
        # self.previousButton = QPushButton("&Previous")
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
        # self.nextButton.clicked.connect(self.mapper.toNext)
        # self.previousButton.clicked.connect(self.mapper.toPrevious)
        # self.mapper.currentIndexChanged.connect(self.updateButtons)
        self.model.row_moved.connect(self.tabBar.swap_tabs)
        #self.model.row_moved.connect(self.tabBar.moveTab)

        self.listButton.clicked.connect(self.animate_listview)

        layout = QGridLayout(self)
        layout.addWidget(self.listButton, 0, 0)
        layout.addWidget(self.listView, 1, 0)
        layout.addWidget(self.tabBar, 0, 1, 1, 1, Qt.AlignTop)
        layout.addWidget(self.textEdit, 1, 1, 1, 1)
        self.setLayout(layout)

        self.setWindowTitle("Simple Widget Mapper")
        self.mapper.toFirst()
        QTimer.singleShot(1000, self.animate_listview)

    def animate_listview(self, start=0, end=300):
        if self.listView.maximumWidth() != 0:
            start, end = end, start
            self.listButton.setArrowType(Qt.RightArrow)
        else:
            self.listButton.setArrowType(Qt.DownArrow)
        anim = QPropertyAnimation(
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

    # @Slot(int)
    # def updateButtons(self, row):
        # self.previousButton.setEnabled(row > 0)
        # self.nextButton.setEnabled(row < self.model.rowCount()-1)


if __name__ == '__main__':
    w = Window()
    w.show()