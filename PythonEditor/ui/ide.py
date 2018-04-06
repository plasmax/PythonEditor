import sys
import imp
from Qt import QtWidgets
from PythonEditor.ui import pythoneditor
from PythonEditor.ui import pythoneditortabs

class IDE(QtWidgets.QWidget):
    """
    Container widget that allows the
    whole package to be reloaded for 
    development purposes.
    """
    def __init__(self, tabs=False):
        super(IDE, self).__init__()
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.setObjectName('IDE')
        self.buildUI(tabs=tabs)

    def buildUI(self, tabs=False):
        if tabs:
            self.pythonEditor = pythoneditortabs.PythonEditorTabs(parent=self)
        else:
            self.pythonEditor = pythoneditor.PythonEditor(parent=self)
        self.layout.addWidget(self.pythonEditor)

    def reload_package(self, tabs=False):
        """
        Reloads the whole package.
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
                # print name
                # del sys.modules[name]

        reload(pythoneditor)
        reload(pythoneditortabs)

        self.buildUI(tabs=tabs)

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
