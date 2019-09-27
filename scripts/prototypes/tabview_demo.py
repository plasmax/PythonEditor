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
from PythonEditor.ui import terminal

from PythonEditor.ui import menubar
from PythonEditor.ui.features import shortcuts
from PythonEditor.ui.features import actions
from PythonEditor.ui.features import autosavexml
from PythonEditor.ui.dialogs import preferences
from PythonEditor.ui.dialogs import shortcuteditor


class PythonEditor(QWidget):
    def __init__(self):
        """ Brings together the data model (currently XMLModel),
        along with several views - Editor, TabView, ListView, and QDataWidgetMapper. 
        """
        super(PythonEditor, self).__init__()
        self.model = XMLModel()

        # create widgets
        self.tab_view = TabView()

        self.editor = Editor()
        self.editor.setFont(QFont('DejaVu Sans'))
        
        self.list_view = ListView()
        # self.list_view.setMaximumWidth(0)
        # self.list_view.resize(50, self.list_view.height())

        self.listButton = QToolButton()
        self.listButton.setArrowType(Qt.DownArrow)
        self.listButton.setFixedSize(24, 24)
        
        # layout
        self.tab_widget = QWidget(self)
        tab_layout = QHBoxLayout(self.tab_widget)
        tab_layout.setContentsMargins(0,0,0,0)
        tab_layout.addWidget(self.tab_view)
        tab_layout.addWidget(self.listButton)
        
        self.bottom_splitter = QSplitter(Qt.Horizontal)
        self.bottom_splitter.addWidget(self.editor)
        self.bottom_splitter.addWidget(self.list_view)
        self.bottom_splitter.setSizes([300,20])
        policy = QSizePolicy.Expanding
        self.bottom_splitter.setSizePolicy(policy, policy)
        
        self.terminal = terminal.Terminal()
        self.tabeditor = QWidget(self)
        bottom_layout = QVBoxLayout(self.tabeditor)
        bottom_layout.setContentsMargins(0,0,0,0)
        bottom_layout.addWidget(self.tab_widget)
        bottom_layout.addWidget(self.bottom_splitter)
        
        layout = QVBoxLayout(self)
        layout.setObjectName(
            'PythonEditor_MainLayout'
        )
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.tabeditor)
        self.setLayout(layout)
        
        splitter = QSplitter(
            Qt.Vertical
        )
        splitter.setObjectName(
            'PythonEditor_MainVerticalSplitter'
        )
        splitter.addWidget(self.terminal)
        splitter.addWidget(self.tabeditor)

        layout.addWidget(splitter)
        self.splitter = splitter

        # act = actions.Actions(
            # pythoneditor=self,
            # editor=self.editor,
            # tabeditor=self.tabeditor,
            # terminal=self.terminal,
        # )

        # sch = shortcuts.ShortcutHandler(
            # editor=self.editor,
            # tabeditor=self.tabeditor,
            # terminal=self.terminal,
        # )

        # self.menubar = menubar.MenuBar(self)

        SE = shortcuteditor.ShortcutEditor
        self.shortcuteditor = SE(
            editor=self.editor,
            tabeditor=self.tabeditor,
            terminal=self.terminal
            )

        PE = preferences.PreferencesEditor
        self.preferenceseditor = PE()

        # set model on views
        self.list_view.setModel(self.model)
        self.tab_view.setModel(self.model)
        
        # add model mapper
        self.mapper = QDataWidgetMapper(self)
        self.mapper.setModel(self.model)
        self.mapper.addMapping(self.editor, 1)

        # connect signals
        self.selection_model = self.list_view.selectionModel()
        self.selection_model.currentRowChanged.connect(self.mapper.setCurrentModelIndex)
        self.tab_view.currentChanged.connect(self.mapper.setCurrentIndex)
        self.tab_view.setSelectionModel(self.selection_model)
        self.editor.modificationChanged.connect(self.submit_and_refocus)
        self.mapper.currentIndexChanged.connect(self.tab_view.setCurrentIndex)
        self.mapper.currentIndexChanged.connect(self.setListIndex)
        self.model.row_moved.connect(self.tab_view.swap_tabs)
        self.listButton.clicked.connect(self.animate_listview)
        
        # get first item from model - this is where we would restore last viewed tab
        self.mapper.toFirst()

        # self.list_view.installEventFilter(self)
        
    # def eventFilter(self, obj, event):
        # print event.type()
        # return super(PythonEditor, self).eventFilter(obj, event)
        
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
        cursor = self.editor.textCursor()
        self.mapper.submit()
        self.editor.setTextCursor(cursor)

    @Slot(int)
    def setListIndex(self, row):
        index = self.model.index(row, 0)
        self.list_view.setCurrentIndex(index)


if __name__ == '__main__':
    w = PythonEditor()
    w.show()
    w.resize(800, 400)