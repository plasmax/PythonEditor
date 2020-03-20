
from PythonEditor.ui.Qt import QtWidgets, QtCore
from PythonEditor.ui.editor import Editor
from functools import partial


class Label():
    def __init__(self):
        super(Label, self).__init__()

class Tabs(QtWidgets.QTabWidget):
    tabs = []
    def __init__(self):
        super(Tabs, self).__init__()
    
    def new_button(self):
        i = self.currentIndex()+1
        e = Editor()
        self.insertTab(i, e, '')
        b = QtWidgets.QToolButton()
        b.editor = e
        b.clicked.connect(self.close_tab)
        self.tabs.append(b)
        b.setText('x')
        l = QtWidgets.QLabel('Widget')
        self.tabs.append(l)
        tb = self.tabBar()
        tb.setTabButton(i, QtWidgets.QTabBar.RightSide, b)
        tb.setTabButton(i, QtWidgets.QTabBar.LeftSide, l)
    
    def close_tab(self):
        tab = self.sender()
        self.removeTab(self.indexOf(tab.editor))

        
t = Tabs()
t.show()

t.new_button()
t.new_button()

class VB(QtCore.QObject):
    s = QtCore.Signal()

v = VB()
v.s


QtCore.Signal