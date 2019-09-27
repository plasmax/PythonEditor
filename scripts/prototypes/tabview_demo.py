
from PythonEditor.ui.Qt.QtCore import QPropertyAnimation, Qt, Slot, QTimer
from PythonEditor.ui.Qt.QtGui import QStandardItem, QFont
from PythonEditor.ui.Qt.QtWidgets import (
    QWidget, 
    QSplitter, 
    QSizePolicy,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QToolButton, 
    QPushButton, 
    QPlainTextEdit, 
    QDataWidgetMapper, 
)

from PythonEditor.ui.editor import Editor
from PythonEditor.ui.tabview import TabView, ListView
from PythonEditor.models.xmlmodel import XMLModel


class TabEditor(QWidget):
    def __init__(self):
        """ Brings together the data model (currently XMLModel),
        along with several views - Editor, TabView, ListView, and QDataWidgetMapper. 
        """
        super(TabEditor, self).__init__()
        self.model = XMLModel()

        # create widgets
        self.tab_view = TabView()

        self.text_edit = Editor()
        self.text_edit.setFont(QFont('DejaVu Sans'))
        
        self.list_view = ListView()
        self.list_view.setMaximumWidth(0)

        self.listButton = QToolButton()
        self.listButton.setArrowType(Qt.DownArrow)
        self.listButton.setFixedSize(24, 24)
        
        # layout
        self.tab_widget = QWidget(self)
        tab_layout = QHBoxLayout(self.tab_widget)
        tab_layout.setContentsMargins(0,0,0,0)
        tab_layout.addWidget(self.tab_view)
        tab_layout.addWidget(self.listButton)
        
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.text_edit)
        self.splitter.addWidget(self.list_view)
        policy = QSizePolicy.Expanding
        self.splitter.setSizePolicy(policy, policy)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.tab_widget)
        layout.addWidget(self.splitter)
        self.setLayout(layout)

        # set model on views
        self.list_view.setModel(self.model)
        self.tab_view.setModel(self.model)
        
        # add model mapper
        self.mapper = QDataWidgetMapper(self)
        self.mapper.setModel(self.model)
        self.mapper.addMapping(self.text_edit, 1)

        # connect signals
        self.selection_model = self.list_view.selectionModel()
        self.selection_model.currentRowChanged.connect(self.mapper.setCurrentModelIndex)
        self.tab_view.currentChanged.connect(self.mapper.setCurrentIndex)
        self.tab_view.setSelectionModel(self.selection_model)
        self.text_edit.modificationChanged.connect(self.submit_and_refocus)
        self.mapper.currentIndexChanged.connect(self.tab_view.setCurrentIndex)
        self.mapper.currentIndexChanged.connect(self.setListIndex)
        self.model.row_moved.connect(self.tab_view.swap_tabs)
        self.listButton.clicked.connect(self.animate_listview)
        
        # get first item from model - this is where we would restore last viewed tab
        self.mapper.toFirst()

    def animate_listview(self, start=0, end=100):
        anim = QPropertyAnimation(
            self.list_view,
            'maximumWidth'
        )
        self._anim = anim
        
        def release():
            self.list_view.setMaximumWidth(2000)
        if self.list_view.maximumWidth() != 0:
            start, end = end, start
            self.listButton.setArrowType(Qt.DownArrow)
        else:
            self.listButton.setArrowType(Qt.RightArrow)
            anim.finished.connect(release)
            
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setDuration(80)
        anim.start()

    @Slot()
    def submit_and_refocus(self):
        cursor = self.text_edit.textCursor()
        self.mapper.submit()
        self.text_edit.setTextCursor(cursor)

    @Slot(int)
    def setListIndex(self, row):
        index = self.model.index(row, 0)
        self.list_view.setCurrentIndex(index)


if __name__ == '__main__':
    w = TabEditor()
    w.show()
    w.resize(800, 400)