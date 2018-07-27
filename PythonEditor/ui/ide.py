import sys
import imp
from PythonEditor.ui.Qt import QtWidgets
from PythonEditor.ui import pythoneditor


class IDE(QtWidgets.QWidget):
    """
    Container widget that allows the whole
    package to be reloaded.
    """
    def __init__(self):
        super(IDE, self).__init__()
        self._layout = QtWidgets.QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setObjectName('IDE')
        self.setWindowTitle('Python Editor')
        self.buildUI()

    def buildUI(self):
        self.pythonEditor = pythoneditor.PythonEditor(parent=self)
        self._layout.addWidget(self.pythonEditor)

    def reload_package(self):
        """
        Reloads the whole package, except for modules
        in the not_reloadable list.
        """
        self.pythonEditor.deleteLater()
        del self.pythonEditor

        not_reloadable = [
                            'PythonEditor.ui.idetabs',
                            'PythonEditor.ui.pythoneditor',
                            'PythonEditor.ui.ide',
                            '__main__'
                         ]

        loaded_modules = sys.modules
        for name, mod in loaded_modules.items():
            if (mod and hasattr(mod, '__file__')
                    and 'PythonEditor' in mod.__file__
                    and name not in not_reloadable):
                imp.reload(mod)

        imp.reload(pythoneditor)

        self.buildUI()

    def showEvent(self, event):
        """
        Hack to get rid of margins automatically put in
        place by Nuke Dock Window.
        """
        try:
            parent = self.parent()
            for x in range(6):
                parent.layout().setContentsMargins(0, 0, 0, 0)
                parent = parent.parent()
        except AttributeError:
            pass

        super(IDE, self).showEvent(event)
