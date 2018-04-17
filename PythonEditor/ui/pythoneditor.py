from PythonEditor.ui.Qt import QtWidgets, QtCore
from PythonEditor.ui.terminal import Terminal
from PythonEditor.ui import shortcuteditor
from PythonEditor.ui import preferenceseditor
from PythonEditor.ui import edittabs
from PythonEditor.utils import save
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
        layout.setContentsMargins(0, 0, 0, 0)

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
        """
        sch = shortcuts.ShortcutHandler(self.edittabs)
        sch.clear_output_signal.connect(self.terminal.clear)
        self.shortcuteditor = shortcuteditor.ShortcutEditor(sch)
        self.preferenceseditor = preferenceseditor.PreferencesEditor()

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
        helpMenu = QtWidgets.QMenu('Help')
        editMenu = QtWidgets.QMenu('Edit')

        for menu in [fileMenu, editMenu, helpMenu]:
            menuBar.addMenu(menu)

        fileMenu.addAction('Save As',
                           self.save_as)

        fileMenu.addAction('Save Selected Text',
                           self.save_selected_text)

        fileMenu.addAction('Export Selected To External Editor',
                           self.export_selected_to_external_editor)

        fileMenu.addAction('Export All Tabs To External Editor',
                           self.export_all_tabs_to_external_editor)

        editMenu.addAction('Preferences',
                           self.show_preferences)
        editMenu.addAction('Shortcuts',
                           self.show_shortcuts)

        helpMenu.addAction('Reload Python Editor',
                           self.parent.reload_package)

        self.layout().addWidget(menuBar)

    def save_as(self):
        cw = self.edittabs.currentWidget()
        save.save_as(cw)

    def save_selected_text(self):
        cw = self.edittabs.currentWidget()
        save.save_selected_text(cw)

    def export_selected_to_external_editor(self):
        cw = self.edittabs.currentWidget()
        save.export_selected_to_external_editor(cw)

    def export_all_tabs_to_external_editor(self):
        save.export_all_tabs_to_external_editor(self.edittabs)

    def show_shortcuts(self):
        """
        Generates a popup dialog listing available shortcuts.
        """
        self.shortcuteditor.show()

    def show_preferences(self):
        """
        Generates a popup dialog listing available preferences.
        """
        self.preferenceseditor.show()

    def showEvent(self, event):
        """
        Hack to get rid of margins automatically put in
        place by Nuke Dock Window.
        """
        try:
            parent = self.parentWidget().parentWidget()
            parent.layout().setContentsMargins(0, 0, 0, 0)

            parent = self.parentWidget().parentWidget().parentWidget().parentWidget()
            parent.layout().setContentsMargins(0, 0, 0, 0)
        except Exception:
            pass

        super(PythonEditor, self).showEvent(event)
