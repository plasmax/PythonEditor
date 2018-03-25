import sys

from Qt import QtWidgets, QtCore, QtGui
from editor import Editor
from terminal import Terminal
from features.shortcuts import ShortcutHandler
from codeeditor.core import execute

class IDE(QtWidgets.QWidget):
    """
    Main widget. 
    Sets up layout and connects 
    some signals.
    """
    def __init__(self):
        super(IDE, self).__init__()
        self.setObjectName('IDE')

        #construct layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setObjectName('IDE_MainLayout')
        layout.setContentsMargins(0,0,0,0)

        self.setup_menu()

        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        splitter.setObjectName('IDE_MainVerticalSplitter')

        self.editor = Editor()
        terminal = Terminal()
        splitter.addWidget(terminal)
        splitter.addWidget(self.editor)

        layout.addWidget(splitter)

        #connect signals
        sch = ShortcutHandler(self.editor)
        sch.execTextSignal.connect(execute.mainexec)
        sch.execTextSignal.connect(terminal.setTabFocus)
        sch.clearOutputSignal.connect(terminal.clear)

    def setup_menu(self):
        """
        Adds top menu bar and various manu items.
        """
        menuBar = QtWidgets.QMenuBar(self)
        fileMenu = QtWidgets.QMenu('File')
        editMenu =  QtWidgets.QMenu('Edit')
        helpMenu =  QtWidgets.QMenu('Help')
        for menu in [fileMenu, editMenu, helpMenu]:
            menuBar.addMenu(menu)

        fileMenu.addAction('Save') #QtGui.QAction (?)
        fileMenu.addAction('Save As')

        editMenu.addAction('Settings')
        editMenu.addAction('Copy to Sublime')
        editMenu.addAction('Open in Sublime')

        helpMenu.addAction('About Python Editor')
        helpMenu.addAction('Shortcuts')

        # self.layout().addWidget(menuBar)
