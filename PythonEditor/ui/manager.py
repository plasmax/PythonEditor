import os

from PythonEditor.ui.Qt import QtWidgets, QtCore, QtGui
from PythonEditor.ui import edittabs
from PythonEditor.ui import browser
from PythonEditor.ui import menubar
from PythonEditor.ui.features import shortcuts
from PythonEditor.ui.features import autosavexml
from PythonEditor.ui.dialogs import preferences
from PythonEditor.ui.dialogs import shortcuteditor
# from PythonEditor import save
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
        self.currently_viewed_file = None
        self.build_layout()

    def build_layout(self):
        """
        Create the layout.
        """
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        # self.setup_menu()
        self.menubar = menubar.MenuBar(self)

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

        self.install_features()

        self.check_modified_tabs()
        if self.tabs.count() == 0:
            self.tabs.new_tab()

    def install_features(self):
        """
        Install features and connect required signals.
        """
        sch = shortcuts.ShortcutHandler(self.tabs)
        # sch.clear_output_signal.connect(self.terminal.clear)
        self.shortcuteditor = shortcuteditor.ShortcutEditor(sch)
        self.preferenceseditor = preferences.PreferencesEditor()

        self.filehandler = autosavexml.AutoSaveManager(self.tabs)

        self.browser.path_signal.connect(self.read)

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

        for index in indices:
            self.update_icon(tab_index=index)

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

    def find_file_tab(self, path):
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
        Read from text file and create associated editor
        if not present. This should replace last viewed file
        if that file has not been edited, to avoid cluttering.
        """
        self.path_edit.setText(path)
        if not os.path.isfile(path):
            return

        tab_index, editor = self.find_file_tab(path)
        already_open = (tab_index is not None)
        if not already_open:
            self.replace_viewed(path)
        else:
            self.tabs.setCurrentIndex(tab_index)
        # if no editor with path in tabs add new
        self.editor = self.tabs.currentWidget()
        self.editor.path = path

        with open(path, 'rt') as f:
            text = f.read()
            self.editor.setPlainText(text)

        doc = self.editor.document()
        doc.modificationChanged.connect(self.modification_handler)
        # self.editor.modificationChanged.connect(self.modification_handler)

    def replace_viewed(self, path):
        """
        Replaces the currently viewed document,
        if unedited, with a new document.
        """
        viewed = self.currently_viewed_file
        self.currently_viewed_file = path

        find_replaceable = (viewed is not None)

        # let's only replace files if they're the current tab
        editor = self.tabs.currentWidget()
        tab_index = self.tabs.currentIndex()
        if hasattr(editor, 'path'):
            if path == viewed:
                find_replaceable = True

        if find_replaceable:
            # tab_index, editor = self.find_file_tab(viewed)

            is_replaceable = (tab_index is not None)
            if is_replaceable:
                with open(viewed, 'rt') as f:
                    file_text = f.read()
                    editor_text = editor.toPlainText()
                    if file_text != editor_text:  # ndiff cool feature
                        is_replaceable = False

            if is_replaceable:
                self.tabs.setCurrentIndex(tab_index)
                self.tabs.setTabText(tab_index, os.path.basename(path))
                return

        filename = os.path.basename(path)
        self.tabs.new_tab(tab_name=filename)

    @QtCore.Slot(bool)
    def modification_handler(self, changed):
        """
        Slot for editor document modificationChanged
        """
        print changed, 'set tab italic!'
        size = 20, 20
        if changed:
            size = 10, 10
        self.update_icon(size=size)

    def update_icon(self, tab_index=None, size=(10, 10)):
        """
        Represent the document's save state
        by setting an icon on the tab.
        """
        if tab_index is None:
            tab_index = self.tabs.currentIndex()
        px = QtGui.QPixmap(*size)
        ico = QtGui.QIcon(px)
        self.tabs.setTabIcon(tab_index, ico)
        # editor = self.tabs.widget(tab)
        # editor.document().setModified(False)

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
