import sys
from functools import partial
from Qt import QtWidgets, QtCore, QtGui
from editor import Editor
from terminal import Terminal

from PythonEditor.ui import shortcuteditor
from PythonEditor.ui import edittabs
from PythonEditor.utils import save
from PythonEditor.utils import constants
from PythonEditor.ui.features import shortcuts
from PythonEditor.ui.features import filehandling

class PythonEditor(QtWidgets.QWidget):
    """
    Main widget. Sets up layout 
    and connects some signals.
    """
    def __init__(self, parent=None):
        super(PythonEditor, self).__init__()
        self.setObjectName('PythonEditor')
        self.parent = parent

        self.construct_ui()
        self.connect_signals()

    def construct_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setObjectName('PythonEditor_MainLayout')
        layout.setContentsMargins(0,0,0,0)

        self.edittabs = edittabs.EditTabs()
        self.terminal = Terminal()

        self.setup_menu()

        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        splitter.setObjectName('PythonEditor_MainVerticalSplitter')
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
        sch = shortcuts.ShortcutHandler(self.edittabs)
        sch.clear_output_signal.connect(self.terminal.clear)
        self.shortcuteditor = shortcuteditor.ShortcutEditor(sch)

        self.filehandler = filehandling.FileHandler(self.edittabs)

    def setup_menu(self):
        """
        Adds top menu bar and various menu items.

        TODO: Implement the following:
        # fileMenu.addAction('Save') #QtGui.QAction (?)

        # editMenu.addAction('Copy to External Editor')
        # editMenu.addAction('Open in External Editor')

        # helpMenu.addAction('About Python Editor')
        """
        menuBar = QtWidgets.QMenuBar(self)
        fileMenu = QtWidgets.QMenu('File')
        helpMenu =  QtWidgets.QMenu('Help')
        editMenu =  QtWidgets.QMenu('Edit')
        
        for menu in [fileMenu, editMenu, helpMenu]:
            menuBar.addMenu(menu)

        save_as = partial(save.save_as, self.edittabs.current_editor)
        fileMenu.addAction('Save As', save_as)

        save_selected = partial(save.save_selected_text, self.edittabs.current_editor)
        fileMenu.addAction('Save Selected Text', save_selected)
        
        export_to_external_editor = partial(save.export_selected_to_external_editor, self.edittabs.current_editor)
        fileMenu.addAction('Export Selected To External Editor', export_to_external_editor)

        editMenu.addAction('Preferences') #TODO: Set up Preferences widget with External Editor path option 
        editMenu.addAction('Shortcuts', self.show_shortcuts)

        helpMenu.addAction('Reload Python Editor', self.parent.reload_package)

        self.layout().addWidget(menuBar)

    def show_shortcuts(self):
        """
        Generates a popup dialog listing available shortcuts.
        TODO: Make this editable, and reassign shortcuts on edit.
        """
        self.shortcuteditor.show()

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

        super(PythonEditor, self).showEvent(event)
