# tabectomy.

"""
Plan: implement a QAbstractListModel that stores the tab data in `list` and `dict` formats.
The QTabBar (or whatever replacement) serves only as a View, a totally interchangeable component. It should mostly be connected via signals.

The only data it stores is the name, tooltip and uid reference: all the meaningful data manipulation takes place on the model.

TODO:
- [ ] Reach parity with existing PythonEditor features
    - [ ] Renamable tabs
    - [ ] Tab close button (that doesn't cause the tab bar to jump)
- [ ] Moving a tab should rearrange the model._list
- [ ] Combo - entering a new tab name could create a new tab!
- [ ] New Tab button
- [ ] Status bar 
    - [ ] show saved status
    - [ ] status out of date with autosave (and menu options to deal with it)
    - [ ] show current file path
- [ ] Combo currentIndexChanged change current tab index, and vice versa - but ___by uid___
- [x] Tab Close Button should be applied in the same way as nameedit (with eventfilter to track mouse movement)
- [ ] Clicking close button should close tab
- [ ] JSON preview/edit autosave file
"""
try:
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
except ImportError:
    from PySide.QtGui import *
    from PySide.QtCore import *


import os
import uuid
from PythonEditor.ui.features.autosavexml import parsexml
from PythonEditor.ui.editor import Editor


UID_ROLE = Qt.UserRole+3
TEXT_ROLE = Qt.UserRole+4
PATH_ROLE = Qt.UserRole+5
SAVED_STATE_ROLE = Qt.UserRole+6


class EditorModel(QAbstractListModel):
    """
    # spec
    # Stores all tab data as a `dict` of `uuid1`: `dict` pairs,
    # and a `list` of those uuids for ordered python2 lookup and
    # easy reordering.
    
    _data = {
        'subscripts' : {},
        uuid1() : {
            'name': 'tab_name',
            'path': 'C:/path/to/file.py',
            'text': 'raw_text',
        },
        uuid1() : {},
        uuid1() : {},
    }
    from pprint import pprint
    pprint(_data, indent=2)
    """
    def __init__(self):
        super(EditorModel, self).__init__()
        self._list = []
        self._data = {}
        self._current_uid = ''

    def rowCount(self, index=QModelIndex()):
        return len(self._list)
        # return max(0, len(self._list)-1)
    
    def data(self, index, role=Qt.DisplayRole):
        count = self.rowCount()
        if not count:
            return
        row = index.row()
        if row >= count:
            return None
        uid = self._list[row]
        if role == UID_ROLE:
            return uid
        elif role == Qt.DisplayRole:
            return self._data[uid]['name']
        elif role == TEXT_ROLE:
            return self._data[uid]['text']
        elif role == PATH_ROLE:
            return self._data[uid]['path']
        elif role == SAVED_STATE_ROLE:
            return self._data[uid]['saved']
        return None
    
    # def setData(
    
    # def headerData(
    
    # def flags(self, index, role=Qt.DisplayRole):
        
        # QAbstractListModel.flags
            
    # -------------------------------- end override methods
    def __len__(self):
        return self.rowCount()
    
    def __iter__(self):
        """for item in self.model()"""
        for uid in self._list:
            yield uid, self._data[uid]
    
    def __getitem__(self, uid):
        """value_dict = self.model()[uid]"""
        return self._data[uid]
    
    def __setitem__(self, uid, value_dict):
        """Allow self.model()[uid] = value_dict """
        if uid in self._list:
            row = self._list.index(uid)
        else:
            row = len(self)
            self._list.append(uid)
            
        index = QModelIndex(row, 0)
        self._data[uid] = value_dict
        self.dataChanged.emit(index, index)
    
    # -------------------------------- end dunder methods
    def populate(self):
        try:
            path = self.get_json_path()
            self.load_from_json_path(path)
            return
        except FileNotFoundError:
            print('Not loading from json yet')

        print('Loading from xml:')
        path = self.get_xml_path()
        self.load_from_xml_path(path)

    def append_data(self, data_list):
        first = len(self)
        last = first + len(data_list) - 1
        # self.beginInsertRows(QModelIndex(), first, last)
        for uid, value_dict in data_list:
            self._list.append(uid)
            self._data[uid] = value_dict
        # self.endInsertRows()
        
        topleft = self.index(first, 0)
        btmrght = self.index(last, 0)
        self.dataChanged.emit(topleft, btmrght)
        
    def raw_data(self):
        return [(key, self._data[key]) for key in self._list]
        
    def get_json_path(self):
        return os.getenv('PYTHONEDITOR_AUTOSAVE_JSON_FILE', '')
    
    def to_json(self):
        return json.dumps(self.raw_data(), indent=2)
        
    def save_to_json_path(self, path):
        """store the json as a list of dicts to preserve order"""
        data = self.to_json()
        with open(path, 'w') as fd:
            data = fd.write(data)
        
    def load_from_json_path(self, path):
        """load json into `list` and lookup `dict`"""
        with open(path, 'r') as fd:
            data = json.load(fd)
        self._data = dict(data)
        self._list = [key for key, _ in data]
    
    def get_xml_path(self):
        return os.getenv('PYTHONEDITOR_AUTOSAVE_FILE', '')
        
    def load_from_xml_path(self, path):
        """load from the old xml format """
        # path = os.getenv('PYTHONEDITOR_AUTOSAVE_FILE', '')
        
        # subscript_data = parsexml('subscripts', path=path) # TODO:
        roow, current_index_elements = parsexml('current_index', path=path)
        for index in current_index_elements:
            current_index = int(index.text)
        
        root, subscripts = parsexml('subscript', path=path)
        
        data_list = []
        for subscript in sorted(subscripts, key=lambda s: s.attrib.get('tab_index')):
            uid = uuid.UUID(subscript.attrib.get('uuid'))
            data = {
                'text': subscript.text,
                'name': subscript.attrib.get('name', ''),
                'path': subscript.attrib.get('path', ''),
                'saved': subscript.attrib.get('saved', False),
            }
            for key, value in subscript.attrib.items():
                if key in data.keys():
                    continue
                elif key == 'uuid':
                    continue
                else:
                    data[key] = value
            data_list.append([uid, data])
            if int(subscript.attrib.get('tab_index')) == current_index:
                self.set_current_uid(uid)
            
        self.append_data(data_list)

    @Slot(int, int)
    def swap_rows(self, a, b):
        self._list[a], self._list[b] = self._list[b], self._list[a]

    def current_uid(self):
        return self._current_uid
    
    @Slot(uuid.UUID)
    def set_current_uid(self, uid):
        self._current_uid = uid


class NameEdit(QLineEdit):
    def __init__(self, parent=None):
        super(NameEdit, self).__init__(parent=parent)
        self.setTextMargins(3,1,3,1)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFocusPolicy(Qt.TabFocus)
    
    def keyPressEvent(self, event):
        QLineEdit.keyPressEvent(self, event)
        if event.key()==Qt.Key_Escape:
            self.hide()


class CloseTabButton(QAbstractButton):
    close_clicked_signal = Signal(int)
    def __init__(self, parent=None, side=QTabBar.RightSide):
        super(CloseTabButton, self).__init__(parent=parent)
        self.side = side
        self.setFocusPolicy(Qt.NoFocus)
        self.setCursor(Qt.ArrowCursor)
        self.setToolTip('Close Tab')
        self.resize(self.sizeHint())
        self.is_moving = False

    def paintEvent(self, event):
        p = QPainter(self)
        opt = QStyleOption()
        try:
            opt.init(self)
        except AttributeError:
            # pyside 1/python 2.7
            opt.initFrom(self)
        opt.state |= QStyle.State_AutoRaise
        if (self.isEnabled() and self.underMouse() and not self.isChecked() and not self.isDown()):
            opt.state |= QStyle.State_Raised
        if (self.isChecked()):
            opt.state |= QStyle.State_On
        if (self.isDown()):
            opt.state |= QStyle.State_Sunken
        tb = self.parent()
        if isinstance(tb, QTabBar):
            index = tb.currentIndex()
            if (tb.tabButton(index, self.side) == self):
                opt.state |= QStyle.State_Selected

        self.style().drawPrimitive(QStyle.PE_IndicatorTabClose, opt, p, self)

    def sizeHint(self):
        self.ensurePolished()
        width = self.style().pixelMetric(QStyle.PM_TabCloseIndicatorWidth)
        height = self.style().pixelMetric(QStyle.PM_TabCloseIndicatorHeight)
        return QSize(width, height)

    def enterEvent(self, event):
        if self.isEnabled():
            self.update()
        QAbstractButton.enterEvent(self, event)

    def leaveEvent(self, event):
        if self.isEnabled():
            self.update()
        QAbstractButton.leaveEvent(self, event)

    def mousePressEvent(self, event):
        super(CloseTabButton, self).mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            parent_pos = self.mapToParent(event.pos())
            index = self.parent().tabAt(parent_pos)
            self._pressed_index = index

    def mouseReleaseEvent(self, event):
        super(CloseTabButton, self).mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            parent_pos = self.mapToParent(event.pos())
            index = self.parent().tabAt(parent_pos)
            if index == self._pressed_index:
                self.close_clicked_signal.emit(index)
                self._pressed_index = -2
    
    def eventFilter(self, obj, event):
        if (obj != self.parent()) or (not isinstance(obj, QTabBar)):
            return False
            
        offset = 0
        if event.type() in [QEvent.MouseButtonPress, QEvent.MouseButtonRelease]:
            self.start_pos = event.pos()
            row = obj.tabAt(self.start_pos)
            rect = obj.tabRect(row)
            self.start_rect = rect
            self.is_moving = False
        elif event.type() == QEvent.MouseMove:
            offset = self.start_pos.x()-event.pos().x()
            rect = self.start_rect
            self.is_moving = True
        elif event.type() in [QEvent.Paint]:
            if self.is_moving:
                return False
            row = obj.currentIndex()
            if row == -1:
                return False
            rect = obj.tabRect(row)
        else:
            return False
        
        position = obj.style().styleHint(QStyle.SH_TabBar_CloseButtonPosition)
        if position == QTabBar.ButtonPosition.RightSide:
            x = rect.topRight().x()-self.width()-5-offset
            y = rect.center().y()-self.rect().center().y()
            pos = QPoint(x, y)
        elif position == QTabBar.ButtonPosition.LeftSide:
            pos = rect.topLeft()
        
        self.move(pos)
        self.raise_()
        
        return False


       
class Bar(QTabBar):
    tab_changed = Signal(uuid.UUID)
    def __init__(self):
        super(Bar, self).__init__()
        self._model = None
        self._current_uid = ''

        self.setMovable(True)
        # self.setUsesScrollButtons(False)
        self.setSelectionBehaviorOnRemove(QTabBar.SelectPreviousTab)
        
        self.line_edit = NameEdit(self)
        self.line_edit.editingFinished.connect(self.name_edited)
        self.line_edit.hide()
        
        self.close_button = CloseTabButton(self)
        self.installEventFilter(self.close_button)
        
        self.currentChanged.connect(self.handle_tab_changed)

    def tabSizeHint(self, index):
        size = QTabBar.tabSizeHint(self, index)
        size.setWidth(size.width()+50)
        # size.setHeight(size.height()+6)
        return size
        
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            index = self.tabAt(event.pos())
            # rect = self.get_close_button_rect(index)
            # if not rect.contains(event.pos()):
            self.show_line_edit(index)
        else:
            QTabBar.mouseDoubleClickEvent(self, event)
            
    # def mousePressEvent(self, event):
        # if event.button()==Qt.LeftButton:
            # self.line_edit.hide()
            
            # index = self.tabAt(event.pos())
            # rect = self.get_close_button_rect(index)
            # if rect.contains(event.pos()):
                # self.close_button_pressed_index = index
                # self.update()
                # return
            # else:
                # self.drag_in_progress = True
                # self.update()
        # elif event.button()==Qt.MidButton:
            # index = self.tabAt(event.pos())
            # self.removeTab(index)
        # QTabBar.mousePressEvent(self, event)
            
    # def mouseReleaseEvent(self, event):
        # if event.button()==Qt.LeftButton:
            # index = self.tabAt(event.pos())
            # rect = self.get_close_button_rect(index)
            # if rect.contains(event.pos()):
                # self.close_button_pressed_index = -1
                # self.update()
                # self.removeTab(index)
                # return
            # else:
                # self.drag_in_progress = False
                # self.update()
        # QTabBar.mouseReleaseEvent(self, event)
    
    def setTabData(self, index, uid):
        """Override: the only data the tab stores is a reference to the model."""
        assert isinstance(uid, uuid.UUID)
        super(Bar, self).setTabData(index, uid)

    # -------------------------------- end override methods
    def show_line_edit(self, index):
        self.line_edit.current_index = index
        rect = self.tabRect(index)
        self.line_edit.setGeometry(rect)
        text = self.tabText(index)
        self.line_edit.setText(text)
        self.line_edit.show()
        self.line_edit.selectAll()
        self.line_edit.setFocus(Qt.MouseFocusReason)
        
    def name_edited(self):
        self.setTabText(self.line_edit.current_index, self.line_edit.text())
        self.line_edit.hide()
        
    def model(self):
        return self._model
    
    def setModel(self, model):
        if self._model is not None:
            self.disconnect_from_model(self._model)
            self.clear()
        
        self._model = model
        self.load_model_data()
        self.connect_to_model(self._model)

    def connect_to_model(self, model):
        model.dataChanged.connect(self.handle_data_changed)
        
    def disconnect_from_model(self, model):
        model.dataChanged.disconnect(self.handle_data_changed)
    
    @Slot(QModelIndex, QModelIndex)
    def handle_data_changed(self, top_left_index, bottom_right_index):
        model = self.model()
        for row in range(top_left_index.row(), bottom_right_index.row()):
            index = model.index(row, 0)
            uid = index.data(UID_ROLE)
            name = index.data(Qt.DisplayRole)
            tab_row = self.get_tab_row_by_uid(uid)
            if tab_row == -1:
                tab_row = self.addTab(name)
                self.setTabData(tab_row, uid)
            if self.tabText(tab_row) != name:
                self.setTabText(tab_row, name)
            path = index.data(PATH_ROLE)
            if path:
                self.setTabToolTip(tab_row, path)
    
    def get_tab_row_by_uid(self, uid):
        for row in range(self.count()):
            if self.tabData(row) == uid:
                return row
        return -1
        
    def load_model_data(self):
        for uid, value_dict in self.model():
            row = self.addTab(value_dict['name'])
            self.setTabData(row, uid)
            path = value_dict.get('path')
            if path:
                self.setTabToolTip(row, path)                
        
    def clear(self, model):
        self.blockSignals(True)
        while self.rowCount():
            self.removeTab(1)
        self.blockSignals(False)

    def current_uid(self):
        return self._current_uid
    
    def set_current_uid(self, uid):
        self._current_uid = uid
        self.tab_changed.emit(uid)

    @Slot(int)
    def handle_tab_changed(self, row):
        uid = self.tabData(row)
        if uid is None:
            return
        if uid != self.current_uid():
            self.set_current_uid(uid)
    
    def set_tab_by_uid(self, uid):
        if not uid:
            return
        row = self.get_tab_row_by_uid(uid)
        if row == -1:
            return
        self.setCurrentIndex(row)


class Combo(QComboBox):
    MIN_WIDTH = 21
    MAX_WIDTH = 200
    def __init__(self):
        super(Combo, self).__init__()
        self.setMaximumWidth(self.MIN_WIDTH)
        self.setEditable(True)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.view().setMinimumWidth(self.MAX_WIDTH)
        
        # TODO: this requires the model to be set up
        # completer = QCompleter(self)
        # self.setCompleter(completer)
    
    # def mousePressEvent(self, event):
        # super(Combo, self).mousePressEvent(event)
        # if event.buttons() == Qt.LeftButton:
            # width = self.MAX_WIDTH if self.maximumWidth() == self.MIN_WIDTH else self.MIN_WIDTH
            # self.setMaximumWidth(width)
            # self.setMinimumWidth(width)


class StatusBar(QStatusBar):
    def showMessage(self, message, timeout=0):
        super(StatusBar, self).showMessage(str(message), timeout=0)
        


class Dialog(QWidget):
    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent=parent)
        if parent is None:
            self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowTitle('Python Editor')
        self.add_widgets()
        self.load()
        self.connect_signals()
        self.restore_state()

    def add_widgets(self):
        self.menubar = QMenuBar()
        self.menubar.addMenu('File')
        
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.top_widget = QWidget()
        self.top_widget.setLayout(QVBoxLayout(self.top_widget))
        top_layout = self.top_widget.layout()
        top_layout.setSpacing(0)
        top_layout.setContentsMargins(0,0,0,0)

        top_layout.addWidget(self.output)
        
        self.bar = Bar()
        self.new_tab_button = QToolButton()
        self.combo = Combo()
        
        self.tab_widget = QWidget()
        self.tab_widget.setLayout(QHBoxLayout(self.tab_widget))
        tab_layout = self.tab_widget.layout()
        tab_layout.setSpacing(0)
        tab_layout.setContentsMargins(0,0,0,0)
        tab_layout.addWidget(self.bar)
        tab_layout.addWidget(self.new_tab_button)
        tab_layout.addWidget(self.combo)
        
        self.editor = Editor()
        self.bottom_widget = QWidget()
        self.bottom_widget.setLayout(QVBoxLayout(self.bottom_widget))
        bottom_layout = self.bottom_widget.layout()
        bottom_layout.setSpacing(0)
        bottom_layout.setContentsMargins(0,0,0,0)
        bottom_layout.addWidget(self.tab_widget)
        bottom_layout.addWidget(self.editor)
        
        self.statusbar = StatusBar()
        
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.addWidget(self.top_widget)
        self.splitter.addWidget(self.bottom_widget)
        
        self.setLayout(QVBoxLayout(self))
        main_layout = self.layout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.addWidget(self.menubar)
        main_layout.addWidget(self.splitter)
        main_layout.addWidget(self.statusbar)
    
    def load(self):
        self.model = EditorModel()
        self.model.populate()
        self.combo.setModel(self.model)
        self.bar.setModel(self.model)
        
    def connect_signals(self):
        self.combo.currentIndexChanged.connect(self.bar.setCurrentIndex)
        self.bar.tab_changed.connect(self.set_editor_contents)
        self.bar.tab_changed.connect(self.statusbar.showMessage)
        self.bar.tab_changed.connect(self.model.set_current_uid)
        self.editor.text_changed_signal.connect(self.update_text_in_model)
        self.bar.tabMoved.connect(self.model.swap_rows)

    def restore_state(self):
        uid = self.model.current_uid()
        self.bar.set_tab_by_uid(uid)

    @Slot(uuid.UUID)
    def set_editor_contents(self, uid):
        self.editor.replace_text(self.model[uid]['text'])
    
    @Slot()
    def update_text_in_model(self):
        uid = self.bar.current_uid()
        if not uid:
            return
        self.model[uid]['text'] = self.editor.toPlainText()


d  = Dialog()
d.show()
self = d

