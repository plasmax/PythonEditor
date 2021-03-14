# replace the Tab Choice menu on the far right with a search box
from __future__ import absolute_import
from __future__ import print_function
from Qt import QtWidgets, QtGui, QtCore
from six.moves import range


class TabComboList(QtWidgets.QComboBox):
    def __init__(self, names=[], tabs=None):
        super(TabComboList, self).__init__()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setInsertPolicy(self.NoInsert)
        self.setEditable(True)
        self._names = names
        self.addItems(names)
        self.tabs = tabs
        #self._comp = QtWidgets.QCompleter(names)
        #self.setCompleter(self._comp)
        #self.editingFinished.connect(self.close)
        #self._comp.highlighted.connect(self.emit_list_index)
        self.currentIndexChanged.connect(self.emit_list_index)
        self.activated.connect(self.handle_activated)
        #cpl = self.completer()
        #cpl.highlighted.connect(self.handle_activated)
        #self.setCompleter(cpl)
        
    def emit_list_index(self, index):
        print(index)
        print(self._names[index])
    
    def handle_activated(self, index):
        print('activated', index)
        self.tabs.tabs.setCurrentIndex(index)
        
    def keyPressEvent(self, event):
        if event.key() in [
            #QtCore.Qt.Key_Return,
            #QtCore.Qt.Key_Enter,
            QtCore.Qt.Key_Escape
        ]:
            self.close()
        super(TabComboList, self).keyPressEvent(event)
        
    def focusOutEvent(self, event):
        super(TabComboList, self).focusOutEvent(event)
        comp = self.completer()
        popup = comp.popup() 
        if popup is not None:
            if not popup.isVisible():
                self.close()

    
def show_tab_menu(self):
    names = [
        self.tabs.tabText(i)
        for i in range(self.tabs.count())
    ]
    if hasattr(self, '_tab_combo_list'):
        tcl = self._tab_combo_list
        if tcl.isVisible():
            tcl.close()
            return
    tcl = self._tab_combo_list = TabComboList(names, self)
    tcl.show()
    b = self.tab_list_button
    g = b.geometry()
    p = b.pos()
    p = g.topLeft()
    p = self.mapToGlobal(p)

    tcl.resize(200, tcl.height())
    tcl.move(p-QtCore.QPoint(200, 0))
    tcl.raise_()
    tcl.setFocus(QtCore.Qt.MouseFocusReason)
    

from functools import partial
self = _ide.python_editor.tabeditor
self.show_tab_menu = partial(show_tab_menu, self)
#tab_list_button.
