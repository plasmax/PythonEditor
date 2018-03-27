import sys

from Qt import QtWidgets, QtCore, QtGui
from editor import Editor
from terminal import Terminal
from features import shortcuts

from edittabs import EditTabs
from features import tabshortcuts

class IDE(QtWidgets.QWidget):
    """
    Main widget. Sets up layout 
    and connects some signals.
    """
    def __init__(self):
        super(IDE, self).__init__()
        self.setObjectName('IDE')

        self.construct_ui()
        self.connect_signals()

    def construct_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setObjectName('IDE_MainLayout')
        layout.setContentsMargins(0,0,0,0)

        self.setup_menu()

        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        splitter.setObjectName('IDE_MainVerticalSplitter')

        self.edittabs = EditTabs()
        self.terminal = Terminal()
        splitter.addWidget(self.terminal)
        splitter.addWidget(self.edittabs)

        layout.addWidget(splitter)

    def connect_signals(self):
        """
        Connect child widget slots to shortcuts.
        TODO: Find a better place to set this up,
        as the shortcuthandler will not be so readily 
        available when the editor is placed inside a 
        TabWidget. Could relay the signal through the 
        TabWidget, or find a global connection mechanism.

        Alternatively, we can dynamically set ShortcutHandler's
        editor widget depending on the TabWidget's current tab.
        (In this case the QShortcut widget is the tabwidget and
        ShortcutContext is WidgetWithChildrenShortcut or WindowShortcut). 
        This would mean keeping the ShortcutHandler here (and avoid 
        creating new shortcut objects for every tab).
        """
        sch = tabshortcuts.ShortcutHandler(self.edittabs)
        sch.clear_output_signal.connect(self.terminal.clear)

    def setup_menu(self):
        """
        Adds top menu bar and various menu items.
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

        self.layout().addWidget(menuBar)

    def showEvent(self, event):
        """
        Hack to get rid of margins automatically put in
        place by Nuke Dock Window.
        """
        try:
            parent = self.parentWidget().parentWidget()
            parent.layout().setContentsMargins(0,0,0,0)

            parent = self.parentWidget().parentWidget().parentWidget().parentWidget()
            parent.layout().setContentsMargins(0,0,0,0)
        except:
            pass

        super(IDE, self).showEvent(event)
