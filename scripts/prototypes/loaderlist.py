from PythonEditor.ui.Qt import QtWidgets, QtGui, QtCore
from PythonEditor.ui import edittabs
from PythonEditor.ui import editor
from PythonEditor.ui.features import autosavexml

QtWidgets.QTabBar.setTabButton
class LoaderList(QtWidgets.QListView): #WIP name

    emit_text = QtCore.Signal(str)
    emit_tab = QtCore.Signal(dict)
    def __init__(self):
        super(LoaderList, self).__init__()
        _model = QtGui.QStandardItemModel()
        self._model = QtGui.QStandardItemModel()
        self.setModel(self._model)

    def __setitem__(self, name, value):
        item = QtGui.QStandardItem(name)
        item.setData(value, role=QtCore.Qt.UserRole+1)
        self._model.appendRow(item)
   
    def selectionChanged(self, selected, deselected):
        #print selected, deselected
        for index in selected.indexes():
            item = self._model.item(index.row(), index.column())
            #print item
            a = item.data(QtCore.Qt.UserRole+1)
            print(a)
            #self.emit_text.emit(text)
            self.emit_tab.emit(a)
            #if index.column() == 0:
        super(LoaderList, self).selectionChanged(
            selected, deselected)

class SingleTab(QtWidgets.QWidget):
    def __init__(self):
        super(SingleTab, self).__init__()
        l = LoaderList()
        self.l = l
        root, subscripts = autosavexml.parsexml('subscript')
        for s in subscripts:
            name = s.attrib.get('name')
            a = s.attrib.copy()
            a['text'] = s.text
            l[name] = a

        self.t = edittabs.EditTabs()
        self.l.emit_tab.connect(self.receive_tab)
        
        self._layout = QtWidgets.QHBoxLayout(self)
        self.splitter = QtWidgets.QSplitter(self)
        self._layout.addWidget(self.splitter)
        self.setLayout(self._layout)
        
        self.splitter.addWidget(self.l)
        self.splitter.addWidget(self.t)

        

    @QtCore.Slot(dict)
    def receive_tab(self, tab):
        # look for temp_tab and replace it if still temp
        editor = self.t.new_tab(tab_name=tab['name'])
        #editor = QtWidgets.QPlainTextEdit()
        #t.insertTab(0, temp_editor, tab['name'])
        text = tab['text']
        editor.path = tab.get('path')
        editor.uid = tab['uuid']
        editor.setPlainText(text)
        editor.temp_tab = True
 
s = SingleTab()
s.show()
"""
#QtCore.QModelIndex.data(1, QtCore.Qt.UserRole)
l = LoaderList()
l.show()

root, subscripts = autosavexml.parsexml('subscript')
for s in subscripts:
    name = s.attrib.get('name')
    a = s.attrib.copy()
    a['text'] = s.text
    l[name] = a
    
#e = editor.Editor()
#e.show()
##l.emit_text.connect(e.setPlainText)


@QtCore.Slot(dict)
def receive_tab(tab):
    # look for temp_tab and replace it if still temp
    editor = t.new_tab(tab_name=tab['name'])
    #editor = QtWidgets.QPlainTextEdit()
    #t.insertTab(0, temp_editor, tab['name'])
    text = tab['text']
    editor.path = tab.get('path')
    editor.uid = tab['uuid']
    editor.setPlainText(text)
    editor.temp_tab = True
 
t = edittabs.EditTabs()
t.show()
l.emit_tab.connect(receive_tab)
"""


"""
w = QtWidgets.QWidget()
l = QtWidgets.QVBoxLayout(w)
s = QtWidgets.QSplitter(w)
l.addWidget(s)
w.show()

d1 = QtWidgets.QDial()
d2 = QtWidgets.QDial()
s.addWidget(d1)
s.addWidget(d2)
"""


"""
t = edittabs.EditTabs()
t.show()


root, subscripts = autosavexml.parsexml('subscript')
for s in subscripts:
    name = s.attrib.get('name')
    l[name] = s.text
    t.insertTab(0, e, name)
    #t.new_tab(tab_name=name)
"""