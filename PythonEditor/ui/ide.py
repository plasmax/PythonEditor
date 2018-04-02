import sys
from functools import partial

from Qt import QtWidgets, QtCore, QtGui
from editor import Editor
from terminal import Terminal
from features import shortcuts
from PythonEditor.utils import save

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


        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        splitter.setObjectName('IDE_MainVerticalSplitter')

        self.editor = Editor()
        self.terminal = Terminal()

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
        sch = shortcuts.ShortcutHandler(self.editor)
        sch.clear_output_signal.connect(self.terminal.clear)
        self.shortcut_dict = sch.shortcut_dict

    def setup_menu(self):
        """
        Adds top menu bar and various menu items.

        TODO: Implement the following:
        editMenu =  QtWidgets.QMenu('Edit')
        for menu in [fileMenu, editMenu, helpMenu]:
            menuBar.addMenu(menu)
        # fileMenu.addAction('Save') #QtGui.QAction (?)

        # editMenu.addAction('Settings')
        # editMenu.addAction('Copy to Sublime')
        # editMenu.addAction('Open in Sublime')

        # helpMenu.addAction('About Python Editor')
        """
        menuBar = QtWidgets.QMenuBar(self)
        fileMenu = QtWidgets.QMenu('File')
        helpMenu =  QtWidgets.QMenu('Help')

        menuBar.addMenu(fileMenu)
        menuBar.addMenu(helpMenu)

        save_as = partial(save.save_as, self.editor)
        fileMenu.addAction('Save As', save_as)

        save_selected = partial(save.save_selected_text, self.editor)
        fileMenu.addAction('Save Selected Text', save_selected)
        
        export_to_sublime = partial(save.export_selected_to_sublime, self.editor)
        fileMenu.addAction('Export Selected To Sublime', export_to_sublime)

        helpMenu.addAction('Show Shortcuts', self.show_shortcuts)
        helpMenu.addAction('Unload Python Editor', self.reload_package)

        self.layout().addWidget(menuBar)

    def show_shortcuts(self):
        """
        Generates a popup dialog listing available shortcuts.
        """
        self.treeView = QtWidgets.QTreeView()
        model = QtGui.QStandardItemModel()
        self.treeView.setModel(model)
        root = model.invisibleRootItem()
        model.setHorizontalHeaderLabels(['Shortcut', 'Description'])
        for item in self.shortcut_dict.items():
            row = [QtGui.QStandardItem(val) for val in item]
            model.appendRow(row)
        self.treeView.show()

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

    def dragEnterEvent(self, event):
        """
        Allow event to pass to the editor.
        """
        event.ignore()
        super(IDE, self).dragEnterEvent(event)

    def reload_package(self):
        """
        Reloads the whole package.
        TODO:
        Make this work!
        """
        self.close()
        loaded_modules = sys.modules
        for name, mod in loaded_modules.items():
            if (mod
                    and hasattr(mod, '__file__') 
                    and 'PythonEditor' in mod.__file__):
                del sys.modules[name]
