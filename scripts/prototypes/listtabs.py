# diversion: how about a QListView that paints tabs?
# this was a GREAT idea!
"""
TODO:
[x] hide scroll bar
[x] move only, don't drop tabs on top of eachother
[x] dropped items should be the selected ones!
[ ] constrain drag/drop moving thing to within layout (like sublime?) :D QListView.gridSize() maybe?
[ ] paint object while moving?? :D properly?
[ ] padding/margins (could be solved in parent layout tbqh)
[ ] delegate stuff - text, close buttons, etc etc
    [ ] italics on referencd scripts (data state/role on the model)
    [ ] file out of date warning on the listview?  a little circle o that denotes out of date (like gchat's "new message")
    [ ] close buttons - rob what I did on the other one
[ ] hover items! (seems to happen automatically on some styles.. I think the option.state is already there)
[ ] Could we try a filesystem model that uses a bunch of temp files in a folder for autosave instead of one massive xml? would make for cleaner export, maybe faster as well?
[ ] Maybe don't .sort() the entire model - there might be a faster way
[ ] make the text on the List view less contrasty
[ ] a little hover label arrow button thingy that lets you animate open/clsoed the side panel. [ > ]
[ ] QDockWidget!
[ ] buttons next to the tab bar
[ ] a treeview under the listview - in the same scrollarea? :D more realistically, it'd all be a treeview with some different item flags for sorting 
[ ] small x close button on the list view too 
[ ] compact mode - a QComboBox instead of tabs/list
"""


try:
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
except ImportError:
    from PySide.QtGui import *
    from PySide.QtCore import *

from PythonEditor.ui.editor import Editor
from PythonEditor.ui.terminal import Terminal

class MoveListView(QListView):
    def __init__(self):
        super(MoveListView, self).__init__()
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(False)
        self._block = False

    def unblock(self):
        # print ('unblock')
        self._block = False
    # great idea but calls selectionchanged :(
    # def dragMoveEvent(self, event):
        # index = self.indexAt(event.pos())
        # if not index.isValid():
            # return
        # selected = self.selectedIndexes()[0]
        # srow, irow = selected.row(), index.row()
        # if srow==irow:
            # return
        # m = self.model()
        # m.insertRow(irow, m.takeRow(srow))
        # selection = self.selectionModel()
        # selection.select(index, QItemSelectionModel.SelectionFlag.ClearAndSelect)
        # event.accept()
    
    def dragMoveEvent(self, event):
        selected = self.selectedIndexes()[0]
        index = self.indexAt(event.pos())
        if not index.isValid():
            return
        srow, irow = selected.data(ORDER_ROLE), index.data(ORDER_ROLE)
        if srow==irow:
            return
        model = selected.model()
        # model.swap(selected, index) # TODO: when this is implemented you won't need the below
        # model = sort_model.sourceModel()
        # QSortFilterProxyModel.sort
        # print(srow, irow, model)
        model.setData(selected, irow, role=ORDER_ROLE)
        model.setData(index, srow, role=ORDER_ROLE)
        model.sort(0)
        # if not self._block:
            # model.sort(0)
            # self._block = True
            # QTimer.singleShot(10, self.unblock)
            
        # QTimer.singleShot(100, lambda: model.sort(0))
        
        return
        m = self.model()
        m.insertRow(irow, m.takeRow(srow))
        selection = self.selectionModel()
        selection.select(index, QItemSelectionModel.SelectionFlag.ClearAndSelect)
        event.accept()
    

class SideListView(MoveListView):
    def __init__(self):
        super(SideListView, self).__init__()
        
        palette = self.palette()
        brush = palette.text()
        color = brush.color().darker(140)
        brush.setColor(color)
        palette.setBrush(QPalette.Text, brush)
        self.setPalette(palette)
        
        # self.setMaximumWidth(200)
        
    # def sizeHint(self):
        # size = super(SideListView, self).sizeHint()
        ## print(size)
        # size.setWidth(min(size.width(), 200))
        # return size
        # dialog.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.MinimumExpanding)
        
        
class TabListView(MoveListView):
    def __init__(self):
        super(TabListView, self).__init__()
        self.setFlow(QListView.LeftToRight)
        # self.setItemDelegate(TabDelegate(self))
        # return
        # self.setFlow(QListView.TopToBottom)
        
        # self.setLayoutMode(QListView.Batched)
        # self.setMovement(QListView.Snap)
        # self.setViewMode(QListView.ViewMode.ListMode)
        
        # self.setMovement(QListView.Movement.Free)
        # self.setGridSize(self.size())
        # self.setGridSize(QSize())
        # self.setAlternatingRowColors(False)
        # self.setViewMode(QListView.ViewMode.IconMode)
        # self.viewMode()
        # self.viewOptions()
        
        self.setSpacing(0)
        self.setContentsMargins(0,0,0,0)
        # self.setFrameShadow(QFrame.Shadow.Raised)
        self.setFrameShape(QFrame.Shape.NoFrame)
        # self.setFrameShape(QFrame.Shape.Box)
        self.setLineWidth(0)
        self.setMidLineWidth(0)
        self.viewport().setAutoFillBackground(False)
        
        # self.dropIndicatorPosition()
        # QAbstractItemView.DropIndicatorPosition.OnViewport
        
        # self.setMouseTracking(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        font = self.font()
        # font.setItalic(False)
        # font.setBold(False)
        font.setPointSizeF(font.pointSizeF()-1)
        self.setFont(font)
        self.setMaximumHeight(23)
        # self.viewport().setAutoFillBackground(True)
        # self.setAttribute(Qt.WA_NoBackground)
        # self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setWindowFlags(Qt.FramelessWindowHint)
        # self.setResizeMode(QListView.Adjust)
        # self.setAutoScroll(True)
        

        self.setItemDelegate(TabDelegate(self))
        
    # def paintEvent(self, event):
        # return

class PythonEditor(QDialog):
    def __init__(self):
        super(PythonEditor, self).__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        self.tab_list = TabListView()
        self.side_list = SideListView()
        self.input = Editor()
        self.output = Terminal()
        self.input.setContentsMargins(0,0,0,0)
        self.output.setContentsMargins(0,0,0,0)
        
        # dock = QDockWidget(self)
        # dock.setWidget

        self.right_widget = QWidget()
        self.right_widget.setContentsMargins(0,0,0,0)
        self.right_widget.setLayout(QVBoxLayout(self.right_widget))
        layout = self.right_widget.layout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.side_list)
        
        self.left_widget = QWidget()
        self.left_widget.setContentsMargins(0,0,0,0)
        self.left_widget.setLayout(QVBoxLayout(self.left_widget))
        layout = self.left_widget.layout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.output)
        layout.addWidget(self.tab_list)
        layout.addWidget(self.input)
        
        self.setLayout(QHBoxLayout(self))
        layout = self.layout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.left_widget)
        layout.addWidget(self.right_widget)
        


class TabDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # super(TabDelegate, self).paint(painter, option, index)

        tabOption = QStyleOptionTab()
        tabOption.rect = option.rect
        tabOption.state = option.state
        QApplication.style().drawControl(QStyle.CE_TabBarTab, tabOption, painter)
        
        textOption = QTextOption()
        textOption.setAlignment(Qt.AlignCenter)
        # textOption.setAlignment(Qt.AlignLeading)
        # textOption.setAlignment(Qt.AlignLeft)
        # Qt.AlignmentFlag.AlignLeading
        # textOption.setFlags(QTextOption.Flag.ShowDocumentTerminator)
        text_rect = QRect(option.rect)
        # text_rect.moveLeft(1)
        text_rect.adjust(-20,0,0,0)
        text = index.data()
        painter.drawText(text_rect, text, textOption)
        # painter.drawText(option.rect, text, textOption)
        # painter.drawText(0x0, 2, 3)

    def sizeHint(self, option, index):
        size = super(TabDelegate, self).sizeHint(option, index)
        # text = index.data()
        width = option.fontMetrics.horizontalAdvance(index.data())
        size.setWidth(width+40)
        size.setHeight(size.height()+15)
        return size



dialog = PythonEditor()
dialog.show()
self = dialog.tab_list
v = dialog.tab_list
l = dialog.side_list


##&& # model bit
class ItemModel(QStandardItemModel):
    pass
    # subclass to support moving items around 
    def supportedDropActions(self):
        return Qt.MoveAction
    def dropMimeData(self, data, action, row, column, parent):
        return False
    
class TextModel(ItemModel):
    pass # here we add submodels for autosave-y file-saving-y stuff

class OrderModel(QSortFilterProxyModel):
    def __init__(self, model):
        super(OrderModel, self).__init__()
        self.setSourceModel(model)
        # self.setDynamicSortFilter(False)
        # self.setDynamicSortFilter(True)
        # m.dynamicSortFilter()
    
    def lessThan(self, source_left, source_right):
        return source_left.data(ORDER_ROLE) < source_right.data(ORDER_ROLE)
    
    def sort(self, column, order=Qt.AscendingOrder):
        # TODO: can sorting be made quicker if we know only two items are changing order?
        return super(OrderModel, self).sort(column, order=Qt.AscendingOrder)
        
    def swap(self, source_left, source_right):
        # somehow sort these
        pass


import string, random
import this
d = {}
for c in (65, 97):
    for i in range(26):
        d[chr(i+c)] = chr((i+13) % 26 + c)
zen ="".join([d.get(c, c) for c in this.s])
zen = zen.replace('-', '').replace('.', '')
words = [' '+w.capitalize()+' ' for w in zen.split()]


ORDER_ROLE = Qt.UserRole+5
m = TextModel()
for i in range(60):
    # name = ''.join(random.choices(string.ascii_letters + string.digits + '_ '*25, k=random.randint(2, 25)))
    name = ''.join(random.choices(words, k=random.randint(1, 5)))
    item = QStandardItem(name)
    item.setData(i, ORDER_ROLE)
    item.setFlags(item.flags()^Qt.ItemIsDropEnabled)
    text = ' '.join(random.choices(words, k=random.randint(10, 100)))
    text_item = QStandardItem(text)
    m.appendRow([item, text_item])

m = OrderModel(m)
v.setModel(m)
l.setModel(m)
l.setSelectionModel(v.selectionModel())
# row = m.takeRow(1)
# m.insertRow(3, m.takeRow(1))
        # self.data_mapper = QDataWidgetMapper(self)
d = QDataWidgetMapper()
d.setModel(m)
# d.addMapping(dialog.tab_list, 0)
# d.addMapping(dialog.input, 0)
d.addMapping(dialog.input, 1)

# m.moveRow(QModelIndex(), 1, QModelIndex(), 0)
# self.moveRow

# d.toNext()
def update_data(index, previous):
    d.setCurrentIndex(index.row())
self.selectionModel().currentChanged.connect(update_data)
#&&

# self.setItemDelegate(None)
self.setItemDelegate(TabDelegate(self))

QProxyStyle # might be a tab color fix on vista?

QApplication.setStyle('windowsvista')
QApplication.setStyle('Fusion')
# QtWidgets.QApplication.setStyle('Fusion')
app.setPalette(nukepalette.getNukePalette())
