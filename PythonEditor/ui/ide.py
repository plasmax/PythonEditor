import sys
import os

PYTHON_EDITOR_MODULES = []

class Finder(object):
    """
    Keep track of pythoneditor modules loaded
    so that they can be reloaded in the same order.
    """
    _can_delete = True
    def find_module(self, name, path=''):
        if 'PythonEditor' not in name:
            return

        global PYTHON_EDITOR_MODULES
        if PYTHON_EDITOR_MODULES is None:
            return
        if name in PYTHON_EDITOR_MODULES:
            return
        if path is None:
            return

        filename = name.split('.').pop()+'.py'
        for p in path:
            if filename in os.listdir(p):
                PYTHON_EDITOR_MODULES.append(name)
                return

def add_to_meta_path():
	sys.meta_path = [
		i for i in sys.meta_path
		if not hasattr(i, '_can_delete')
	]
	sys.meta_path.append(Finder())
add_to_meta_path()

import imp
from PythonEditor.ui.Qt import QtWidgets
from PythonEditor.ui.Qt import QtCore
from PythonEditor.ui import pythoneditor


class IDE(QtWidgets.QWidget):
    """
    Container widget that allows the whole
    package to be reloaded.
    """
    def __init__(self, parent=None):
        super(IDE, self).__init__(parent)
        self.setLayout(
            QtWidgets.QHBoxLayout(self)
        )
        self.layout().setContentsMargins(
            0, 0, 0, 0
        )
        self.setObjectName('IDE')
        self.setWindowTitle('Python Editor')
        self.buildUI()

    def buildUI(self):
        PE = pythoneditor.PythonEditor
        self.python_editor = PE(parent=self)
        self.layout().addWidget(self.python_editor)

    def reload_package(self):
        """
        Reloads the whole package (except for
        this module), in an order that does not
        cause errors.
        """
        self.python_editor.terminal.stop()
        self.python_editor.deleteLater()
        del self.python_editor

        # reload modules in the order
        # that they were loaded in
        for name in PYTHON_EDITOR_MODULES:
            mod = sys.modules.get(name)
            if mod is None:
                continue
            try:
                imp.reload(mod)
            except ImportError:
                msg = 'could not reload %s: %s'
                print(msg % (name, mod))

        QtCore.QTimer.singleShot(1, self.buildUI)

    def showEvent(self, event):
        """
        Hack to get rid of margins
        automatically put in place
        by Nuke Dock Window.
        """
        try:
            parent = self.parent()
            for x in range(6):
                parent.layout(
                    ).setContentsMargins(
                    0, 0, 0, 0
                )
                parent = parent.parent()
        except AttributeError:
            pass

        super(IDE, self).showEvent(event)
