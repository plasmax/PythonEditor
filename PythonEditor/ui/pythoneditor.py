import sys
from functools import partial

from Qt import QtWidgets, QtCore, QtGui
from terminal import Terminal
from features import shortcuts
from PythonEditor.utils import save
from PythonEditor.utils import constants
from PythonEditor.ui import editor
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

        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        splitter.setObjectName('PythonEditor_MainVerticalSplitter')

        self.editor = editor.Editor(handle_shortcuts=True)
        self.filehandler = filehandling.FileHandler(self.editor)
        self.terminal = Terminal()

        editor_path = constants.get_external_editor_path()
        if not editor_path:
            constants.set_external_editor_path()

        self.setup_menu()

        splitter.addWidget(self.terminal)
        splitter.addWidget(self.editor)

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
        rco = self.editor.relay_clear_output_signal
        rco.connect(self.terminal.clear)

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

        save_as = partial(save.save_as, self.editor)
        fileMenu.addAction('Save As', save_as)

        save_selected = partial(save.save_selected_text, self.editor)
        fileMenu.addAction('Save Selected Text', save_selected)
        
        export_to_external_editor = partial(save.export_selected_to_external_editor, self.editor)
        fileMenu.addAction('Export Selected To External Editor', export_to_external_editor)

        editMenu.addAction('Preferences') #TODO: Set up Preferences widget with External Editor path option 
        editMenu.addAction('Shortcuts', self.show_shortcuts)

        helpMenu.addAction('Reload Python Editor', self.parent.reload_package)
        helpMenu.addAction('Load Python Editor With Tabs', partial(self.parent.reload_package, True))

        self.layout().addWidget(menuBar)

    def show_shortcuts(self):
        """
        Generates a popup dialog listing available shortcuts.
        TODO: Make this editable, and reassign shortcuts on edit.
        """
        self.editor.shortcuteditor.show()

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
