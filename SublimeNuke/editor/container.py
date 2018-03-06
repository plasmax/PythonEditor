import os
import sys
from functools import partial

import time
print 'importing', __name__, 'at', time.asctime()

try:
    import PySide
except:
    sys.path.append('C:/Users/Max-Last/.nuke/python/external')
from PySide import QtGui, QtCore

from features import autocompletion

class Container(QtGui.QTabWidget):

    def __init__(self, file, _globals={}, _locals={}):
        QtGui.QTabWidget.__init__(self)
        self._globals = _globals
        self._locals = _locals
        self.setTabsClosable(True)
        self.new_tab(file=file)
        self._build_tabs()
        self.tabCloseRequested.connect(self.closeTab)

    def _build_tabs(self):
        # create the "new tab" tab with button
        self.insertTab(1, QtGui.QWidget(),'')
        nb = self.new_btn = QtGui.QToolButton()
        nb.setText('+') # you could set an icon instead of text
        nb.setAutoRaise(True)
        nb.clicked.connect(self.new_tab)
        self.tabBar().setTabButton(1, QtGui.QTabBar.RightSide, nb)

    def new_tab(self, file=None):
        index = self.count() - 1
        editContainer = InputContainer(file, 
                        self._globals, self._locals)
        self.insertTab(index, 
            editContainer, 
            'New Tab' if file==None else os.path.basename(file))
        self.setCurrentIndex(index)

    def closeTab(self, index):
        _index = self.currentIndex()
        self.removeTab(index)
        index = self.count() - 1
        self.setCurrentIndex(_index-1)


class InputContainer(QtGui.QWidget):
    """Contains a new code input widget"""
    def __init__(self, file, _globals={}, _locals={}):
        super(InputContainer, self).__init__()
        
        if file == None:
            user = os.environ.get('USERNAME')
            file = 'C:/Users/{}/.nuke/sublimenuke.txt'.format(user)
            with open(file, 'a') as f:
                f.write('')
                f.close()

        if os.path.isfile(file):
            self.editLayout = QtGui.QVBoxLayout(self)

            self.filePath = QtGui.QLineEdit()

            self.editLayout.addWidget(self.filePath)

            self._codeEditor = autocompletion.CodeEditorAuto(file, _globals, _locals)
            self.editLayout.addWidget(self._codeEditor)

            self.filePath.setText(file)

            with open(file.replace('.pyc', '.py'), 'r') as f:
                text = f.read()
            self._codeEditor.setPlainText(text)
