import os

from PythonEditor.ui.Qt import QtWidgets, QtCore, QtGui
from PythonEditor.ui import shortcuteditor
from PythonEditor.ui import preferenceseditor
from PythonEditor.ui import edittabs
from PythonEditor.utils import save
from PythonEditor.ui import browser
from PythonEditor.ui.features import shortcuts
from PythonEditor.ui.features import filehandling
from PythonEditor.utils.constants import NUKE_DIR


def get_parent(widget, level=1):
    """
    Return a widget's nth parent widget.
    """
    parent = widget
    for p in range(level):
        parent = parent.parentWidget()
    return parent


class Manager(QtWidgets.QWidget):
    """
    Layout that connects code editors to a file system
    that allows editing of multiple files and autosaves.
    """
    def __init__(self):
        super(Manager, self).__init__()
        self.build_layout()

    def build_layout(self):
        """
        Create the layout.
        """
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setup_menu()

        left_widget = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_widget)

        path_edit = QtWidgets.QLineEdit()
        path_edit.textChanged.connect(self.update_tree)
        self.path_edit = path_edit

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter = splitter

        self.xpanded = False
        self.setLayout(layout)
        self.tool_button = QtWidgets.QToolButton()
        self.tool_button.setText('<')
        self.tool_button.clicked.connect(self.xpand)
        self.tool_button.setMaximumWidth(20)

        layout.addWidget(splitter)

        browse = browser.FileTree(NUKE_DIR)
        self.browser = browse
        left_layout.addWidget(self.path_edit)
        left_layout.addWidget(self.browser)

        self.tabs = edittabs.EditTabs()

        widgets = [left_widget,
                   self.tool_button,
                   self.tabs]
        for w in widgets:
            splitter.addWidget(w)

        splitter.setSizes([200, 10, 800])

        self.connect_signals()

        self.check_modified_tabs()
        if self.tabs.count() == 0:
            self.tabs.new_tab()

    def connect_signals(self):
        """
        Connect child widget slots to shortcuts.
        """
        sch = shortcuts.ShortcutHandler(self.tabs)
        # sch.clear_output_signal.connect(self.terminal.clear)
        self.shortcuteditor = shortcuteditor.ShortcutEditor(sch)
        self.preferenceseditor = preferenceseditor.PreferencesEditor()

        self.filehandler = filehandling.FileHandler(self.tabs)

        self.browser.path_signal.connect(self.read)

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
        menuBar.setMaximumHeight(30)
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

        fileMenu.addAction('Export Current Tab To External Editor',
                           self.export_current_tab_to_external_editor)

        fileMenu.addAction('Export All Tabs To External Editor',
                           self.export_all_tabs_to_external_editor)

        # helpMenu.addAction('Reload Python Editor',
        #                    self.parent.reload_package)

        editMenu.addAction('Preferences',
                           self.show_preferences)

        editMenu.addAction('Shortcuts',
                           self.show_shortcuts)

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

    def export_current_tab_to_external_editor(self):
        save.export_current_tab_to_external_editor(self.edittabs)

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

    def check_modified_tabs(self):
        """
        On open, check to see which documents are
        not matching their files (if they have them)
        """
        indices = []
        for tab_index in range(self.tabs.count()):
            editor = self.tabs.widget(tab_index)
            if not editor.objectName() == 'Editor':
                continue

            if not hasattr(editor, 'path'):
                # document not yet saved
                indices.append(tab_index)
                continue

            if not os.path.isfile(editor.path):
                # file does not exist
                indices.append(tab_index)
                continue

            with open(editor.path, 'rt') as f:
                if f.read() != editor.toPlainText():
                    indices.append(tab_index)

        print indices
        for index in indices:
            self.set_tab_changed_icon(tab_index=index)

    def xpand(self):
        """
        Expand or contract the QSplitter
        to show or hide the file browser.
        """
        if self.xpanded:
            symbol = '<'
            sizes = [200, 10, 800]  # should be current sizes
        else:
            symbol = '>'
            sizes = [0, 10, 800]  # should be current sizes

        self.tool_button.setText(symbol)
        self.splitter.setSizes(sizes)
        self.xpanded = not self.xpanded

    @QtCore.Slot(str)
    def update_tree(self, path):
        """
        Update the file browser when the
        lineedit is updated.
        """
        model = self.browser.model()
        root_path = model.rootPath()
        if root_path in path:
            return
        path = os.path.dirname(path)
        if not os.path.isdir(path):
            return
        path = path+os.altsep
        print path
        self.browser.set_model(path)

    def find_opened_file(self, path):
        """
        Search currently opened tabs for an editor
        that matches the given file path.
        """
        for tab_index in range(self.tabs.count()):
            editor = self.tabs.widget(tab_index)
            if hasattr(editor, 'path') and editor.path == path:
                return tab_index, editor

        return None, None

    @QtCore.Slot(str)
    def read(self, path):
        """
        Read from text file and create
        associated editor if not present.
        """
        tab_index, editor = self.find_opened_file(path)
        if tab_index is None:
            filename = os.path.basename(path)
            self.tabs.new_tab(tab_name=filename)
        else:
            self.tabs.setCurrentIndex(tab_index)
        # if no editor with path in tabs add new
        self.editor = self.tabs.currentWidget()
        self.editor.path = path
        # self.editor.textChanged.connect(self.text_changed)
        if not os.path.isfile(path):
            return

        with open(path, 'rt') as f:
            text = f.read()
            self.editor.setPlainText(text)
            self.path_edit.setText(path)

        doc = self.editor.document()
        doc.modificationChanged.connect(self.modification_handler)
        # self.editor.modificationChanged.connect(self.modification_handler)

    @QtCore.Slot(object)
    def text_changed(self, *args):
        print args

    @QtCore.Slot(bool)
    def modification_handler(self, changed):
        """
        """
        print changed, 'set tab italic!'
        size = 20, 20
        if changed:
            size = 10, 10
        self.set_tab_changed_icon(size=size)

    def set_tab_changed_icon(self, tab_index=None, size=(10, 10)):
        """
        Visually notify if the document has been
        altered or is different from the editor's
        file by setting an icon on the tab.
        """
        if tab_index is None:
            tab_index = self.tabs.currentIndex()
        px = QtGui.QPixmap(*size)
        ico = QtGui.QIcon(px)
        self.tabs.setTabIcon(tab_index, ico)
        # editor = self.tabs.widget(tab)
        # editor.document().setModified(False)

    @QtCore.Slot(str)
    def write(self):
        """
        Write to text file associated with editor.
        """
        self.editor = self.tabs.currentWidget()
        if not hasattr(self.editor, 'path'):
            return

        path = self.editor.path
        if not os.path.isfile(path):
            raise Exception(path+' is not a file. should create it!')

        with open(path, 'wt') as f:
            f.write(self.editor.toPlainText())

    def showEvent(self, event):
        """
        Hack to get rid of margins automatically put in
        place by Nuke Dock Window.
        """
        try:
            for i in 2, 4:
                parent = get_parent(self, level=i)
                parent.layout().setContentsMargins(0, 0, 0, 0)
        except Exception:
            pass

        super(Manager, self).showEvent(event)
