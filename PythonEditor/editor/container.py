import os
import sys
from functools import partial

import time
print 'importing', __name__, 'at', time.asctime()

from ..qt import QtGui, QtCore
from ..constants import NUKE_DIR

from features import autocompletion

style = """
QTabWidget::pane { /* The tab widget frame */
border-top: 2px solid #C2C7CB;
}
QTabWidget::tab-bar {
left: 5px; /* move to the right by 5px */
/* Style the tab using the tab sub-control. Note that it reads QTabBar _not_ QTabWidget */
QTabBar::tab {
background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #E1E1E1, stop: 0.4 #DDDDDD, stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
border: 2px solid #C4C4C3;
border-bottom-color: #C2C7CB; /* same as the pane color */
border-top-left-radius: 4px;
border-top-right-radius: 4px;
min-width: 8ex;
padding: 2px;
}
QTabBar::tab:selected, QTabBar::tab:hover {
background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #fafafa, stop: 0.4 #f4f4f4, stop: 0.5 #e7e7e7, stop: 1.0 #fafafa);
}
QTabBar::tab:selected {
border-color: #9B9B9B;
border-bottom-color: #C2C7CB; /* same as pane color */
}
QTabBar::tab:!selected {
margin-top: 2px; /* make non-selected tabs look smaller */
}
/* IMPORTANT: 8< Add the code above here 8< */ 
QTabBar::tab:selected { /* expand/overlap to the left and right by 4px */ margin-left: -4px; margin-right: -4px; } 
QTabBar::tab:first:selected { margin-left: 0; /* the first selected tab has nothing to overlap with on the left */ } 
QTabBar::tab:last:selected { margin-right: 0; /* the last selected tab has nothing to overlap with on the right */ } 
QTabBar::tab:only-one { margin: 0; /* if there is only one tab, we don't want overlapping margins */ }
"""

class Container(QtGui.QTabWidget):

    def __init__(self, file, output):
        QtGui.QTabWidget.__init__(self)
        self._output = output
        self.setTabsClosable(True)
        self.new_tab(file=file)
        self._build_tabs()
        self.tabCloseRequested.connect(self.closeTab)
        # self.setStyleSheet(style)

    def _build_tabs(self):
        self.insertTab(1, QtGui.QWidget(),'')
        nb = self.new_btn = QtGui.QToolButton()
        nb.setText('+') # you could set an icon instead of text
        nb.setAutoRaise(True)
        nb.clicked.connect(self.new_tab)
        self.tabBar().setTabButton(1, QtGui.QTabBar.RightSide, nb)

    @QtCore.Slot(str)
    def new_tab(self, file=None):
        index = self.count() - 1
        editContainer = InputContainer(file, self._output)
        print file, type(file)
        self.insertTab(index, 
            editContainer, 
            'New Tab' if file==None else os.path.basename(str(file)))
        self.setCurrentIndex(index)

    def closeTab(self, index):
        _index = self.currentIndex()
        self.removeTab(index)
        index = self.count() - 1
        self.setCurrentIndex(_index-1)

    @QtCore.Slot()
    def relayClearInput(self):
        print 'clear!'

class InputContainer(QtGui.QWidget):
    """Contains a new code input widget"""
    def __init__(self, file, output):
        super(InputContainer, self).__init__()
        
        if file == None:
            file = NUKE_DIR + '/py_editor_temp.txt'
            with open(file, 'a') as f:
                f.write('')
                f.close()
        else:
            file = str(file)

        if os.path.isfile(file):
            self.editLayout = QtGui.QVBoxLayout(self)

            self.filePath = QtGui.QLineEdit()

            self.editLayout.addWidget(self.filePath)

            self._codeEditor = autocompletion.CodeEditorAuto(file, output)
            self.editLayout.addWidget(self._codeEditor)

            self.filePath.setText(file)
