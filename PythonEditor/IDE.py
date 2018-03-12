from __future__ import print_function
import os
import sys
from functools import partial
from pprint import pprint

sys.path.append( os.path.dirname(__file__) ) #add package level path to avoid relative imports
import time
print('importing', __name__, 'at', time.asctime())

from qt import QtGui, QtCore
from constants import NUKE_DIR, AUTOSAVE_FILE

from browser import NukeMiniBrowser
from output import Redirector
from editor import container

class IDE(QtGui.QWidget):
    """
    Main window when running externally.
    """
    def __init__(self):
        super(IDE, self).__init__()

        self.layout = QtGui.QVBoxLayout(self)
        self.setToolTip('Python Editor')
        self._setup()

    def _setup(self):
        self.splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.layout.setContentsMargins(0,0,0,0)

        self.browser = NukeMiniBrowser.FileBrowser(NUKE_DIR)
        self.browser.resize(200, self.browser.height())

        file = self.setupHistoryFile()
        self.output = Redirector.Terminal()
        self.input = container.Container(file, self.output)
        
        use_splitter = False
        if use_splitter:
            self.topsplitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
            self.topsplitter.addWidget(self.browser)
            self.topsplitter.addWidget(self.output)
            self.splitter.addWidget(self.topsplitter)
        else:
            self.toptab = QtGui.QTabWidget()
            self.toptab.addTab(self.output, 'Output')
            self.toptab.addTab(self.browser, 'Browser')
            self.toptab.addTab(QtGui.QTreeWidget(), 'Object Inspector')
            self.toptab.addTab(QtGui.QWidget(), 'Preferences')
            self.toptab.addTab(QtGui.QWidget(), 'Recent Files List')
            self.splitter.addWidget(self.toptab)

        self.splitter.addWidget(self.input)

        self.layout.addWidget(self.splitter)

        #signals
        self.browser.pathSignal.connect(self.input.new_tab)
    
    def setupHistoryFile(self):
        file = AUTOSAVE_FILE
        fileexists = os.path.isfile(file)
        if fileexists:
            return file
        elif not fileexists:
            print("FILE DOESN'T EXIST!")
            if os.path.isdir(NUKE_DIR):
                with open(file, 'w') as f:
                    f.write('<?xml version="1.0" encoding="UTF-8"?><script></script>')
                    f.close()
                return file

    def showEvent(self, event):
        try:
            parent = self.parentWidget().parentWidget()
            parent.layout().setContentsMargins(0,0,0,0)

            parent = self.parentWidget().parentWidget().parentWidget().parentWidget()
            parent.layout().setContentsMargins(0,0,0,0)
        except:
            pass

        super(IDE, self).showEvent(event)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ide = IDE()

    try:
        import qdarkstyle
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyside())
    except ImportError:
        qdarkstyledir = os.path.join(os.path.dirname(__file__), 'qdarkstyle')
        if os.path.isdir(qdarkstyledir):
            sys.path.append(qdarkstyledir)
            import qdarkstyle
            app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt())
            print('QDarkStyle not found')

    ide.show()
    app.exec_()
