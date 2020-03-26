""" The IDE is a top-level container class that
houses the pythoneditor interface. The point of this
class is to make all subsequent modules fully reloadable from
within the PythonEditor UI for development purposes.

Example usage:
from PythonEditor.ui import ide

integrated_development_environment = ide.IDE()
integrated_development_environment.show()
"""
import os
import sys
import traceback

if (sys.version_info.major >= 3
    and sys.version_info.minor >= 4):
    from importlib import reload as reload_module
else:
    from imp import reload as reload_module

PYTHON_EDITOR_MODULES = []

# define this before importing PythonEditor modules.
class Finder(object):
    """ Keep track of pythoneditor modules loaded
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


# imports here now that we are done modifying importer
from PythonEditor.ui.Qt.QtWidgets import QWidget, QHBoxLayout
from PythonEditor.ui.Qt.QtCore import QTimer, Qt
from PythonEditor.ui import pythoneditor


class IDE(QWidget):
    """ Container widget that allows the whole
    package to be reloaded, apart from this module.
    """
    def __init__(self, parent=None):
        super(IDE, self).__init__(parent)
        self.setLayout(
            QHBoxLayout(self)
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
        """ Reloads the whole package (except for
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

            path = mod.__file__
            if path.endswith('.pyc'):
                path = path.replace('.pyc', '.py')
            if not os.path.isfile(path):
                continue
            with open(path, 'r') as f:
                data = f.read()
            if '\x00' in data:
                msg = 'Cannot load {0} due to Null bytes. Path:\n{1}'
                print(msg.format(mod, path))
                continue
            try:
                code = compile(data, mod.__file__, 'exec')
            except SyntaxError:
                # This message only shows in terminal
                # if this environment variable is set:
                # PYTHONEDITOR_CAPTURE_STARTUP_STREAMS
                error = traceback.format_exc()
                msg = 'Could not reload due to the following error:'
                def print_error():
                    print(msg)
                    print(error)
                QTimer.singleShot(100, print_error)
                continue
            try:
                reload_module(mod)
            except ImportError:
                msg = 'could not reload {0}: {1}'
                print(msg.format(name, mod))

        QTimer.singleShot(1, self.buildUI)
        QTimer.singleShot(10, self.set_editor_focus)

    def set_editor_focus(self):
        """ Set the focus inside the editor.
        """
        try:
            retries = self.retries
        except AttributeError:
            self.retries = 0

        if self.retries > 4:
            return

        if not hasattr(self, 'python_editor'):
            QTimer.singleShot(100, self.set_editor_focus)
            self.retries += 1
            return

        editor = self.python_editor.tabeditor.editor
        if not editor.isVisible():
            QTimer.singleShot(100, self.set_editor_focus)
            self.retries += 1
            return
        editor.focus_in_signal.emit()

    def showEvent(self, event):
        """ Hack to get rid of margins
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
