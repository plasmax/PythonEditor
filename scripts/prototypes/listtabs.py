# diversion: how about a QListView that paints tabs?
# this was a GREAT idea!
"""
TODO:
[x] hide scroll bar
[x] move only, don't drop tabs on top of eachother
[x] dropped items should be the selected ones!
[ ] constrain drag/drop moving thing to within layout (like sublime?) :D QListView.gridSize() maybe? WHAT IS THAT THING? IT HOVERS OVER EVERYTHING!! possibly from startDrag()? yes - it's a QDrag.setPixmap from 
    https://stackoverflow.com/questions/2419445/qt-controlling-drag-behaviour
    it might be better to do this with mouseMoveEvent and paintEvent on the SideListView. seems like indexAt(pos), etc would be useful.
    maybe swap visually but don't sort it until you drop?
    or - implement a QAbstractItemModel that can reorder two items easily (how fast can python swap two indices in a huge list?)
[ ] paint object while moving?? :D properly?
[x] padding/margins (could be solved in parent layout tbqh)
[ ] delegate stuff - text, close buttons, etc etc
    [x] italics on referenced scripts (data state/role on the model)
    [x] file out of date warning on the listview?  a little circle o that denotes out of date (like gchat's "new message")
    [x] close buttons - rob what I did on the other one
[ ] hover items! (seems to happen automatically on some styles.. I think the option.state is already there)
[ ] Could we try a filesystem model that uses a bunch of temp files in a folder for autosave instead of one massive xml? would make for cleaner export, maybe faster as well?
[ ] Maybe don't .sort() the entire model - there might be a faster way
[x] make the text on the List view less contrasty
[ ] a little hover label arrow button thingy that lets you animate the side panel open/closed . [ > ]
[ ] QDockWidget!
[ ] <> buttons next to the tab bar
[ ] a treeview under the listview - in the same scrollarea? join them together with 0 spacing to make it look like sublime :D filesystem access!! <3
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


ORDER_ROLE = Qt.UserRole+5
READ_ONLY_ROLE = Qt.UserRole+6
MODIFIED_ROLE = Qt.UserRole+7


class MoveListView(QListView):
    def __init__(self):
        super(MoveListView, self).__init__()
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(False)
        self.setMouseTracking(True)
        self.setSelectionBehavior(QListView.SelectionBehavior.SelectItems)

        self.setSpacing(0)
        self.setContentsMargins(0,0,0,0)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setLineWidth(0)
        self.setMidLineWidth(0)
        
        # self.setFocusPolicy(Qt.NoFocus) # FIXME: this means you can't use up/down arrows on the sidelist!
        
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
        # model.swap(index, selected)
        # model.swap(irow, srow)
        # return
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
    


class MoveTreeView(QTreeView):
    def __init__(self):
        super(MoveTreeView, self).__init__()

        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(False)
        self.setMouseTracking(True)
        self._block = False

        self.setContentsMargins(0,0,0,0)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setLineWidth(0)
        self.setMidLineWidth(0)

# class SideListView(MoveTreeView):
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
        self.setItemDelegate(SideListDelegate(self))
        
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
        self.setFocusPolicy(Qt.NoFocus) # FIXME: this means you can't use up/down arrows on the sidelist!
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
        
        # self.setFrameShadow(QFrame.Shadow.Raised)
        # self.setFrameShape(QFrame.Shape.Box)
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


class PythonEditor(QDialog):
    def __init__(self):
        super(PythonEditor, self).__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setContentsMargins(0,0,0,0)
        
        self.tab_list = TabListView()
        self.side_list = SideListView()
        self.input = Editor()
        self.input.setFrameShape(QFrame.NoFrame)
        # self.input.setLineWidth(0)
        # self.input.setContentsMargins(0,0,0,0)
        self.output = Terminal()
        self.output.setFrameShape(QFrame.NoFrame)
        # self.output.setLineWidth(0)
        # self.output.setContentsMargins(0,0,0,0)
        
        # dock = QDockWidget(self)
        # dock.setWidget

        self.right_widget = QWidget()
        # dialog.left_widget.frameGeometry()
        # rect = dialog.right_widget.frameGeometry()
        # rect.adjusted(-10,0,0,0)
        # dialog.right_widget.setGeometry(rect.adjusted(-5,0,0,0))
        self.right_widget.setContentsMargins(0,0,0,0)
        self.right_widget.setLayout(QVBoxLayout(self.right_widget))
        layout = self.right_widget.layout()
        # layout.setMargin(0)
        # layout.setSpacing(0)
        layout.setContentsMargins(1,0,1,0)
        layout.addWidget(self.side_list)
        
        self.left_widget = QWidget()
        self.left_widget.setContentsMargins(0,0,0,0)
        self.left_widget.setLayout(QVBoxLayout(self.left_widget))
        layout = self.left_widget.layout()
        # layout.setMargin(0)
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.output)
        layout.addWidget(self.tab_list)
        layout.addWidget(self.input)
        
        self.setLayout(QHBoxLayout(self))
        layout = self.layout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.left_widget)
        layout.addWidget(self.right_widget)
        # layout = dialog.layout()
        # layout.insertStretch( -1, 1 )
        layout.setSpacing(0)
        

class FileItemDelegate(QStyledItemDelegate):
    """Implement methods that would be common to an item
    that is going to represent a file, including painting 
    close buttons, text and indicators."""
    close_clicked = Signal(QModelIndex)
    def __init__(self, parent=None):
        super(FileItemDelegate, self).__init__(parent=parent)
        self._close_button_hovered_row = -1
        self._close_button_pressed_row = -1
        self._padding = 10
        self._pressed = False

    def editorEvent(self, event, model, option, index):
            
        if event.type()==QEvent.MouseMove:
            if self._pressed:
                # if self.on_close_button(option, event):
                    # return True
                return False
            if self.on_close_button(option, event):
                self._close_button_hovered_row = index.row()
            else:
                self._close_button_hovered_row = -1
            return True
        elif event.type() in [QEvent.MouseButtonPress, QEvent.MouseButtonDblClick]:
            if event.button()==Qt.LeftButton:
                self._pressed = True
                if self.on_close_button(option, event):
                    self._close_button_pressed_row = index.row()
                    # self._close_button_hovered_row = index.row()
                    return True
                else:
                    self._close_button_pressed_row = -1
        elif event.type()==QEvent.MouseButtonRelease:
            if event.button()==Qt.LeftButton:
                if self.on_close_button(option, event):
                    if index.row() == self._close_button_pressed_row:
                        self.close_clicked.emit(index)
                        model.sourceModel().takeRow(index.row()) # FIXME: you should let the model do this - send the above signal to the model.
                self._pressed = False
                self._close_button_pressed_row = -1
        return False
        
    def paint(self, painter, option, index):
        # if option.state & QStyle.State_MouseOver:
            # print('mouse overrrr')
            # painter.fillRect(option.rect, QColor(0,0,0,10))
        self.draw_text(painter, option, index)
        # self.draw_close_button(painter, option, index)
        self.draw_sublime_close_button(painter, option, index)
        # super(FileItemDelegate, self).paint(painter, option, index)

    def draw_text(self, painter, option, index):
        textOption = QTextOption()
        # textOption.setAlignment(Qt.AlignLeading)
        # Qt.AlignmentFlag.AlignLeading
        # textOption.setFlags(QTextOption.Flag.ShowDocumentTerminator)
        align_left = True
        if align_left:
            textOption.setAlignment(Qt.AlignLeft)
            text_rect = QRect(option.rect)
            text_height = option.fontMetrics.height()
            text_rect.adjust(self._padding, (option.rect.height()/2)-(text_height/2), 0, 0)
        else:
            textOption.setAlignment(Qt.AlignCenter)
            text_rect = QRect(option.rect)
            text_rect.adjust(-20,0,0,0)
        
        if not index.data(MODIFIED_ROLE): # READ_ONLY_ROLE
            font = option.font
            font.setItalic(True)
            painter.setFont(font)
        
        text = index.data()
        painter.drawText(text_rect, text, textOption)
        # painter.drawText(option.rect, text, textOption)
        # painter.drawText(0x0, 2, 3)

    def draw_close_button(self, painter, option, index):
        opt = QStyleOption()
        opt.rect = self.get_close_button_rect(option)
        
        opt.state = option.state

        row = index.row()
        if self._close_button_pressed_row == row:
            opt.state |= QStyle.State_Sunken
        elif self._close_button_hovered_row == row:
            opt.state |= QStyle.State_MouseOver
            opt.state |= QStyle.State_Raised
        else:
            opt.state = QStyle.State_Enabled
        
        QApplication.style().drawPrimitive(QStyle.PE_IndicatorTabClose, opt, painter)
        
    def draw_sublime_close_button(self, painter, option, index):
        opt = QStyleOptionViewItem(option)
        opt.rect = self.get_close_button_rect(option)
        
        rect = QRect(opt.rect)
        rect.setSize(rect.size()/1.2)
        left_line = QLine(rect.topLeft(), rect.bottomRight())
        right_line = QLine(rect.topRight(), rect.bottomLeft())
        
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.HighQualityAntialiasing)

        paint_x = True
        row = index.row()
        # if option.state & QStyle.State_Selected:
        if self._pressed and (self._close_button_pressed_row == row):
            # paint me a sunken X
            brush = QBrush(QColor.fromRgbF(0.2,0.2,0.2,1))
            painter.setBrush(brush)
        # elif (option.state & QStyle.State_MouseOver) and (self._close_button_hovered_row == row):
        elif self._close_button_hovered_row == row:
            # paint me a bright thick X (maybe with a light square or circle underneath?) :)
            painter.fillRect(opt.rect.adjusted(-4,-4,2,2), QColor.fromRgbF(1,1,1,0.02))
            
            brush = option.palette.text()
            pen = QPen(brush, 2)
            painter.setPen(pen)
            rect.moveCenter(rect.center()+QPoint(0.5,0.5))
        elif index.data(MODIFIED_ROLE):
            # paint me a filled circle o
            # for the "not saved"/"document modified" state
            paint_x = False
            path = QPainterPath()
            path.addEllipse(rect)
            painter.fillPath(path, QBrush(QColor.fromRgbF(1,1,1,0.5)))
        else:
            brush = option.palette.light()
            pen = QPen(brush, 1.2)
            painter.setPen(pen)
            
        if paint_x:
            # paint me a normal X
            painter.drawLine(left_line)
            painter.drawLine(right_line)
        
        painter.restore()
        
    def get_close_button_rect(self, option):
        h = option.rect.height()-15#/2
        rect = QRect(0, 0, h, h)
        pos = QPoint(option.rect.right(), option.rect.center().y())
        # pos -= QPoint((rect.width()/2)+self._padding, 0)
        pos -= QPoint((rect.width()/2)+self._padding, 0)
        rect.moveCenter(pos)
        return rect
        # return QRect(-25, h-8, 16, 16).translated(option.rect.topRight())
    
    def on_close_button(self, option, event):
        rect = self.get_close_button_rect(option)
        pos = event.pos()
        return rect.contains(pos)


class SideListDelegate(FileItemDelegate):
    def paint(self, painter, option, index):
        # return QStyledItemDelegate.paint(self, painter, option, index) # for testing
        opt = QStyleOptionViewItem(option)
        # rect = QRect(opt.rect)
        opt.rect.moveLeft(16)
        QStyledItemDelegate.paint(self, painter, opt, index)
        # super(SideListDelegate, self).paint(painter, option, index)
        self.draw_sublime_close_button(painter, option, index)
        
    def get_close_button_rect(self, option):
        # return QRect(-25, h-8, 16, 16).translated(option.rect.topRight())
        h = option.rect.height()-7
        rect = QRect(0, 0, h, h)
        pos = QPoint(option.rect.left(), option.rect.center().y())
        # pos -= QPoint((rect.width()/2)+self._padding, 0)
        pos -= QPoint((rect.width()/2)-self._padding, 0)
        rect.moveCenter(pos)
        rect.moveLeft(8)
        return rect
    

class TabDelegate(FileItemDelegate):
    def sizeHint(self, option, index):
        size = super(TabDelegate, self).sizeHint(option, index)
        # text = index.data()
        try:
            get_width = option.fontMetrics.horizontalAdvance
        except AttributeError:
            # python 2.7 & earlier versions of PySide2
            get_width = option.fontMetrics.width
            
        width = get_width(index.data())
        size.setWidth(width+40)
        size.setHeight(size.height()+15)
        return size
        
    def paint(self, painter, option, index):
        self.draw_tab(painter, option, index)
        super(TabDelegate, self).paint(painter, option, index)

    def draw_tab(self, painter, option, index):
        tabOption = QStyleOptionTab()
        tabOption.rect = option.rect
        tabOption.state = option.state
        QApplication.style().drawControl(QStyle.CE_TabBarTab, tabOption, painter)


dialog = PythonEditor()
dialog.show()
self = dialog.tab_list
v = dialog.tab_list
l = dialog.side_list

# ---------------------------------------- separate here if only doing view stuff above

##&& # model bit
class ItemModel(QStandardItemModel):
    pass
    # subclass to support moving items around 
    def supportedDropActions(self):
        return Qt.MoveAction
    def dropMimeData(self, data, action, row, column, parent):
        return False


class TextModel(ItemModel):
    # here we add submodels for autosave-y file-saving-y stuff
    def __init__(self, parent=None):
        super(TextModel, self).__init__(parent=None)
        # self.beginMoveRows(
        
        ## signals
        # self.dataChanged.connect(self.handle_data_changed)

    # def handle_data_changed(self, topLeft, bottomRight, roles=[]):
        # if topLeft != bottomRight:
            ## one at a time
            # return
        # if topLeft.column() != 1:
            ## only the text/content column
            # return
        # for role in roles:
            ## only edit or display roles
            # if role not in [Qt.DisplayRole, Qt.EditRole]:
                # return
        # self.set_modified(topLeft)
        
    # def set_modified(self, index):
        # sibling = index.sibling(index.row(), 0)
        # self.setData(sibling, True, role=MODIFIED_ROLE)
        # self.dataChanged.emit(sibling, sibling)


class OrderModel(QSortFilterProxyModel):
    def __init__(self, model):
        super(OrderModel, self).__init__()
        self.setSourceModel(model)
        self.setSortRole(ORDER_ROLE)
        # self.setDynamicSortFilter(False)
        # self.setDynamicSortFilter(True)
        # m.dynamicSortFilter()
    
    # def lessThan(self, source_left, source_right):
        # return source_left.data(ORDER_ROLE) < source_right.data(ORDER_ROLE)
    
    # def sort(self, column, order=Qt.AscendingOrder):
        ## TODO: can sorting be made quicker if we know only two items are changing order?
        # return super(OrderModel, self).sort(column, order=Qt.AscendingOrder)
        
    # def swap(self, source_left, source_right):
        
        # self.sourceModel().insertRow(source_left.row(), self.sourceModel().takeRow(source_right.row())) # nope :(
        # return
        ## swap le data
        # data1 = self.itemData(source_left)
        # data2 = self.itemData(source_right)

        # self.setItemData(source_left, data2)
        # self.setItemData(source_right, data1)
        # return
        
        ## somehow sort these
        # model = self.sourceModel()
        # row = source_right.row()
        # lrow = source_left.row()
        # if row==lrow:
            # return
        # print(row, lrow)
        # ok = model.beginMoveRows(QModelIndex(), row, row, QModelIndex(), lrow)
        # if not ok:
            # return
        # model.endMoveRows()

        ## m.sourceModel().beginMoveRows(QModelIndex(), 1, 2, QModelIndex())
        # return
        # self.sourceModel().changePersistentIndex(source_left, source_right)






import string, random
import this
d = {}
for c in (65, 97):
    for i in range(26):
        d[chr(i+c)] = chr((i+13) % 26 + c)
zen ="".join([d.get(c, c) for c in this.s])
zen = zen.replace('-', '').replace('.', '')
words = [' '+w.capitalize()+' ' for w in zen.split()]
try:
    random.choices
except AttributeError:
    def choices(population, k=1):
        # poor man's choices
        count = len(population)
        for z in range(k):
            i = random.randint(0, count-1)
            yield population[i]
    random.choices = choices


m = TextModel()
for i in range(60):
    # name = ''.join(random.choices(string.ascii_letters + string.digits + '_ '*25, k=random.randint(2, 25)))
    name = ''.join(random.choices(words, k=random.randint(1, 5)))
    item = QStandardItem(name)
    item.setData(i, ORDER_ROLE)
    # item.setData('x', Qt.DecorationRole)
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

class DataMapper(QDataWidgetMapper):
    def __init__(self, model):
        super(DataMapper, self).__init__()
        self.setModel(model)
        self.setSubmitPolicy(QDataWidgetMapper.SubmitPolicy.ManualSubmit)
        self._just_updated_row = -1
        
    # def setModel(self, model): # override
        # if self.model() == model:
            # return;
        # if self.model():
            # disconnect(d->model, SIGNAL(dataChanged(QModelIndex,QModelIndex,QVector<int>)), this,
                       # SLOT(_q_dataChanged(QModelIndex,QModelIndex,QVector<int>)));
            # disconnect(d->model, SIGNAL(destroyed()), this,
                       # SLOT(_q_modelDestroyed()));
        
        # self.clearMapping()
        # d->rootIndex = QModelIndex();
        # d->currentTopLeft = QModelIndex();
        # d->model = model;
        # connect(model, SIGNAL(dataChanged(QModelIndex,QModelIndex,QVector<int>)),
                # SLOT(_q_dataChanged(QModelIndex,QModelIndex,QVector<int>)));
        # connect(model, SIGNAL(destroyed()), SLOT(_q_modelDestroyed()));
    
    # def _q_dataChanged(self, topLeft, const QModelIndex &bottomRight, const QVector<int> &):
        # if (topLeft.parent() != rootIndex)
            # return; // not in our hierarchy
        # for (WidgetMapper &e : widgetMap) {
            # if (qContainsIndex(e.currentIndex, topLeft, bottomRight))
                ## TODO: here is where we override population, so that the Editor doesn't get updated again after it updates the model.
                # populate(e);
        
    @Slot()
    def submit_text_change(self):
        # submit is too aggressive - we need to call the model's setData without invoking dataChanged()
        row = self.currentIndex()
        if row == self._just_updated_row:
            self._just_updated_row = -1
            return
        editor = self.mappedWidgetAt(1)
        model = self.model()
        title_index = model.index(row, 0)
        text_index = model.index(row, 1)
        # model.sourceModel().set_modified(text_index)
        model.setData(text_index, editor.toPlainText(), role=Qt.DisplayRole) # FIXME: updating the model updates the editor again (QDataWidgetMapper.populate)
        model.setData(title_index, True, role=MODIFIED_ROLE)
        # print('update!')
    
    def update_data(self, index, previous):
        row = index.row()
        self._just_updated_row = row
        self.setCurrentIndex(row)


# question: is datamapper overkill? it's kind of nice, but I could connect text_changed_signal to the model (or selectionModel?) QItemSelectionModel
d = DataMapper(m)
d.addMapping(dialog.input, 1)
dialog.input.text_changed_signal.connect(d.submit_text_change) 
self.selectionModel().currentChanged.connect(d.update_data)
selection_model = self.selectionModel()

