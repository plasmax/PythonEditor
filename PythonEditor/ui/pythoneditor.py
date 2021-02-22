""" This module contains the main PythonEditor.
It has all the functionality of PythonEditor
except the ability to fully reload the whole package,
which is kept in the container object.

Example usage:
from PythonEditor.ui import pythoneditor

python_editor = pythoneditor.PythonEditor()
python_editor.show()
"""
from PythonEditor.ui.Qt import QtWidgets, QtCore
from PythonEditor.ui import terminal
from PythonEditor.ui import tabs
from PythonEditor.ui import menubar
from PythonEditor.ui.features import shortcuts
from PythonEditor.ui.features import actions
from PythonEditor.ui.features import autosavexml


class PythonEditor(QtWidgets.QWidget):
    """ Main widget. Sets up layout
    and connects some signals.
    """
    def __init__(self, parent=None):
        super(
            PythonEditor,
            self
        ).__init__(parent=parent)
        self.setObjectName('PythonEditor')
        self._parent = parent
        if parent is not None:
            self.setParent(parent)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setObjectName(
            'PythonEditor_MainLayout'
        )
        layout.setContentsMargins(0, 0, 0, 0)

        self.tabeditor = tabs.TabEditor(self)
        self.editor = self.tabeditor.editor
        self.terminal = terminal.Terminal()

        splitter = QtWidgets.QSplitter(
            QtCore.Qt.Vertical
        )
        splitter.setObjectName(
            'PythonEditor_MainVerticalSplitter'
        )
        splitter.addWidget(self.terminal)
        splitter.addWidget(self.tabeditor)

        layout.addWidget(splitter)
        self.splitter = splitter

        act = actions.Actions(
            pythoneditor=self,
            editor=self.editor,
            tabeditor=self.tabeditor,
            terminal=self.terminal,
        )

        self.menubar = menubar.MenuBar(self)
        self.shortcuthandler = shortcuts.ShortcutHandler(
            editor=self.editor,
            tabeditor=self.tabeditor,
            terminal=self.terminal,
        )

		# Loading the AutosaveManager will also load
        # all the contents of the autosave into tabs.
        self.filehandler = autosavexml.AutoSaveManager(self.tabeditor)