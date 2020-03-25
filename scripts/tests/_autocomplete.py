#!/net/homes/mlast/Desktop nuke-tg-python
""" For testing independently. """
from __future__ import absolute_import
import sys
import os


sys.dont_write_bytecode = True
TESTS_DIR = os.path.dirname(__file__)
PACKAGE_PATH = os.path.dirname(TESTS_DIR)
sys.path.append(PACKAGE_PATH)

try:
    import nuke
    pyside = ('PySide' if (nuke.NUKE_VERSION_MAJOR < 11) else 'PySide2')
except ImportError:
    pyside = 'PySide'

os.environ['QT_PREFERRED_BINDING'] = pyside

from PythonEditor.ui.features import nukepalette
from PythonEditor.ui.features import autocompletion
from PythonEditor.ui import editor
from PythonEditor.ui.Qt import QtWidgets


class TestEditor(editor.Editor):
    """
    An override of Editor to strip out other features.
    """
    def __init__(self):
        super(editor.Editor, self).__init__()
        self._changed = False
        self.autocomplete_overriding = True
        self.autocomplete = autocompletion.AutoCompleter(self)

if __name__ == '__main__':
    # """
    # For testing outside of nuke.
    # """
    # try:
    #     app = QtWidgets.QApplication(sys.argv)
    # except RuntimeError:
    #     # for running inside and outside of Nuke
    #     app = QtWidgets.QApplication.instance()

    # e = TestEditor()
    # app.setPalette(nukepalette.getNukePalette())
    # e.show()
    # e.resize(500, 800)
    # plastique = QtWidgets.QStyleFactory.create('Plastique')
    # QtWidgets.QApplication.setStyle(plastique)
    # sys.exit(app.exec_())
