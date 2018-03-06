from __future__ import print_function
import os
import sys
from functools import partial

import time
print(['importing', __name__, 'at', time.asctime()])

try:
    import PySide
except:
    sys.path.append('C:/Users/Max-Last/.nuke/python/external')
from PySide import QtGui, QtCore


if globals().has_key('init_modules'):
    for m in [x for x in sy.modules.keys() if x not in init_modules]:
        print(sys.modules[m] )
        del sys.modules[m]
else:
    init_modules = sys.modules.keys()

from browser import NukeMiniBrowser
reload(NukeMiniBrowser)

from output import terminal
reload(terminal)

from editor import container
reload(container)

from editor import base
reload(base)

from editor.features import linenumbers
reload(linenumbers)

from editor.features import autocompletion
reload(autocompletion)

LEVEL_TWO = True

class IDE(QtGui.QWidget):
    """docstring for IDE"""
    def __init__(self, _globals={}, _locals={}):
        super(IDE, self).__init__()
        self._globals = _globals
        self._locals = _locals
        self.layout = QtGui.QVBoxLayout(self)
        # self.setStyleSheet('background:#282828;color:#fff;') # Main Colors
        self._setup(_globals, _locals)

    def _setup(self, _globals, _locals):
        self.splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.layout.setContentsMargins(0,0,0,0)

        # self.browser = NukeMiniBrowser.FileBrowser('C:/Users/{}/.nuke/'.format(user))
        # self.browser.resize(200, self.browser.height())
        # self.splitter.addWidget(self.browser)

        file = 'C:/Users/tsalx/.nuke/sublimenuke/sublimenuke.txt'
        self.input = container.Container(file, 
                        self._globals, self._locals) #replace with tabwidget

        self.output = terminal.Terminal()
        
        self.splitter.addWidget(self.output)
        self.splitter.addWidget(self.input)

        self.layout.addWidget(self.splitter)
        
    def showEvent(self, event):

        if 'nuke' in globals():
            parent = self.parentWidget().parentWidget()
            parent.layout().setContentsMargins(0,0,0,0)

            parent = self.parentWidget().parentWidget().parentWidget().parentWidget()
            parent.layout().setContentsMargins(0,0,0,0)

        self.output._setup()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ide = IDE()
    ide.show()
    app.exec_()
