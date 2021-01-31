from __future__ import print_function
import math
from PythonEditor.ui.Qt import QtWidgets, QtCore, QtGui


ACTION_ROLE = QtCore.Qt.UserRole+11


class KeyCatcher(QtWidgets.QLineEdit):
    def keyPressEvent(self, event):
        event.accept()
        key = event.key()
        if key in [QtCore.Qt.Key_Control, QtCore.Qt.Key_Alt, QtCore.Qt.Key_Meta, QtCore.Qt.Key_Shift]:
            key = int(event.modifiers())
        else:
            key += int(event.modifiers())

        keyseq = QtGui.QKeySequence(key)
        text = keyseq.toString()

        self.setText(text)


class ShortcutModel(QtGui.QStandardItemModel):
    def __init__(self, handler=None, parent=None):
        super(ShortcutModel, self).__init__(parent=parent)

        labels = ['Description', 'Shortcut', 'About']
        self.setHorizontalHeaderLabels(labels)
        if handler is not None:
            self.load_from_handler(handler)
        
    def load_from_handler(self, handler):
        self._shortcut_handler = handler
        rows = []
        for shortcut, action in handler.shortcut_dict.items():
            rows.append([action.text(), shortcut, action.toolTip(), action])
        for action in handler.unassigned:
            rows.append([action.text(), '', action.toolTip(), action])

        self.add_rows(rows)
    
    def add_rows(self, rows):
        root = self.invisibleRootItem()
        for name, shortcut, about, action in rows:
            name_item = QtGui.QStandardItem(name)
            shortcut_item = QtGui.QStandardItem(shortcut)
            shortcut_item.setData(action, ACTION_ROLE)
            about = self.single_line_description(about)
            # print(about)
            about_item = QtGui.QStandardItem(about)
            # about_item.setData(about, QtCore.Qt.DecorationRole)
            row = [name_item, shortcut_item, about_item]
            root.appendRow(row)
    
    def single_line_description(self, text):
        lines = []
        for line in text.splitlines():
            lines.append(line.strip())
        return ' '.join(lines).strip()

        self.setHorizontalHeaderLabels(
            ['Description', 'Shortcut', 'About']
        )

    def set_shortcut(self, index, value, role=QtCore.Qt.DisplayRole):
        if (index.column() != 1) or (role != QtCore.Qt.EditRole):
            # not a shortcut
            return

        self.setData(index, value, role)

        # unassign shortcut if it was previously assigned
        if value in self._shortcut_handler.shortcut_dict.keys():
            old_action = self._shortcut_handler.shortcut_dict[value]
            old_action.setShortcut(QtGui.QKeySequence())

            # remove it from the shortcuts dict and  
            # add it to the unassigned list
            del self._shortcut_handler.shortcut_dict[value]
            if old_action not in self._shortcut_handler.unassigned:
                self._shortcut_handler.unassigned.append(old_action)

            print('Removed shortcut %r from %r'%(value, old_action.text()))

        new_action = index.data(ACTION_ROLE)
        # remove any existing shortcuts associated with this action
        for shortcut in new_action.shortcuts():
            s = shortcut.toString()
            if s in self._shortcut_handler.shortcut_dict:
                del self._shortcut_handler.shortcut_dict[s]

        key_seq = QtGui.QKeySequence.fromString(value)
        new_action.setShortcut(key_seq)

        # set the shortcut on the handler, so it'll be caught by the eventFilter.
        self._shortcut_handler.shortcut_dict[value] = new_action

        # remove action from the unassigned list
        if new_action in self._shortcut_handler.unassigned:
            self._shortcut_handler.unassigned.remove(new_action)

        print('Set shortcut for %r to %r'%(new_action.text(), key_seq.toString()))


class ShortcutDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super(ShortcutDelegate, self).__init__(parent=parent)
        
    def createEditor(self, parent, option, index):
        editor = KeyCatcher(parent)
        return editor

    def setEditorData(self, editor, index):
        text = index.model().data(index, QtCore.Qt.EditRole)
        editor.setText(text)

    def setModelData(self, editor, model, index):
        new_shortcut = editor.text()
        if new_shortcut==index.data(QtCore.Qt.EditRole):
            # no change
            return

        # don't allow duplicate shortcuts
        if not self.shortcut_already_in_use(editor, model, index):
            model.set_shortcut(index, new_shortcut, role=QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
        
    def eventFilter(self, obj, event):
        if event.type()==QtCore.QEvent.KeyPress:
            if event.key()==QtCore.Qt.Key_Tab:
                if isinstance(obj, KeyCatcher):
                    obj.keyPressEvent(event)
                    return True
        return False
    
    def shortcut_already_in_use(self, editor, model, index):
        """Return `False` if the shortcut is not found 
        on any other actions, otherwise `True`.

        If it is found, show a dialog asking the user if they 
        want to use the shortcut for the current action instead.

        If the user wants to replace, return `True`.
        """
        new_shortcut = editor.text()
        if not new_shortcut:
            return False

        duplicates = {}
        this_column = index.column()
        this_row = index.row()
        for row in range(model.rowCount()):

            if row == this_row:
                continue
            row_index = model.index(row, this_column)
            shortcut = row_index.data(QtCore.Qt.EditRole)
            if shortcut != new_shortcut:
                continue

            name = model.index(row, 0).data(QtCore.Qt.EditRole)
            duplicates[name] = row
        if not duplicates:
            return False

        other_action_names = ', '.join(duplicates.keys())
        msg = 'Replace shortcut %s on %s?' % (new_shortcut, other_action_names)
        buttons = QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No
        widget = self.parent()
        title = 'Duplicate Shortcut(s)'
        decision = QtWidgets.QMessageBox.question(widget, title, msg, buttons=buttons)

        if decision == QtWidgets.QMessageBox.Yes:
            # Remove all duplicate shortcuts 
            for row in duplicates.values():
                row_index = model.index(row, this_column)
                model.setData(row_index, '', QtCore.Qt.EditRole)
            return False
        else:
            return True


class ItemWordWrap(QtWidgets.QStyledItemDelegate):
    update_viewport = QtCore.Signal()
    def __init__(self, parent=None):
        super(ItemWordWrap, self).__init__(parent=parent)
        self.column_width = 100
        
    @QtCore.Slot(int,int,int)
    def handle_column_resized(self, logicalIndex, oldSize, newSize):
        if logicalIndex==2:
            self.column_width = newSize
            self.update_viewport.emit()

    def sizeHint(self, option, index):
        text = index.data()
        fontmetrics = option.fontMetrics

        try:
            get_width = fontmetrics.horizontalAdvance
        except AttributeError:
            # python 2.7 & earlier versions of PySide2
            get_width = fontmetrics.width

        width = get_width(text)
        
        column_width = self.column_width
        chars_per_line = 250
        while (width > column_width) and (chars_per_line > 10):
            width = get_width(text, chars_per_line)
            chars_per_line -= 10

        num_lines = math.ceil(len(text)/chars_per_line)+0.5
        height = fontmetrics.height()
        height *= num_lines
        
        size = QtCore.QSize()
        size.setWidth(width)
        size.setHeight(height)
        
        # FIXME: the below causes recursion. we do want to figure out a way
        # to have the row height adjusted though. this just isn't it yet.
        # index.model().setData(index, size, QtCore.Qt.SizeHintRole)
        # index.model().dataChanged.emit(index, index) 

        return size 


class ShortcutEditor(QtWidgets.QTreeView):
    """
    A display widget that allows editing of
    keyboard shortcuts assigned to the editor.
    """
    def __init__(self, handler=None, parent=None):
        super(ShortcutEditor, self).__init__(parent=parent)
        self.setWindowTitle('Shortcuts')
        self.setWindowFlags(QtCore.Qt.Dialog)
        self.setSortingEnabled(True)
        self.setTextElideMode(QtCore.Qt.ElideNone)
        self.setUniformRowHeights(False)
        self.setWordWrap(True)
        self.setEditTriggers(QtWidgets.QTreeView.SelectedClicked|QtWidgets.QTreeView.DoubleClicked)
        
        self.header().setStretchLastSection(False)

        model = ShortcutModel(handler=handler)
        self.setModel(model)

        # delegates
        self._delegate = ShortcutDelegate()
        self.setItemDelegateForColumn(1, self._delegate)

        self._label_delegate = ItemWordWrap(self)
        self.setItemDelegateForColumn(2, self._label_delegate)
        
        # signals
        self.header().sectionResized.connect(self._label_delegate.handle_column_resized)
        self._label_delegate.update_viewport.connect(self.update_viewport)

        self.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.resize(800, 600)
        for i in range(self.model().columnCount()):
            self.resizeColumnToContents(i)
        self.setColumnWidth(2, 400)

    def update_viewport(self, *args):
        self.viewport().update()


if __name__ == '__main__':
    handler = QtWidgets.QApplication.activeWindow().findChild(QtCore.QObject, 'ShortcutHandler')
    editor = ShortcutEditor(handler=handler)
    editor.show()

