#!/net/homes/mlast/bin nuke-safe-python-tg
""" For testing independently. """
from __future__ import absolute_import
import sys
import os


sys.dont_write_bytecode = True
TESTS_DIR = os.path.dirname(__file__)
PACKAGE_PATH = os.path.dirname(TESTS_DIR)
sys.path.append(PACKAGE_PATH)

if __name__ == '__main__':
    """
    For testing outside of nuke.
    """
    import time
    start = time.time()

    try:
        import nuke
        pyside = (
            'PySide'
            if (nuke.NUKE_VERSION_MAJOR < 11)
            else 'PySide2'
        )
    except ImportError:
        pyside = 'PySide'

    os.environ['QT_PREFERRED_BINDING'] = pyside

    from PythonEditor.ui import ide
    from PythonEditor.ui.features import nukepalette
    from PythonEditor.ui.Qt import QtWidgets, QtGui

    try:
        app = QtWidgets.QApplication(sys.argv)
    except RuntimeError:
        # for running inside and outside of Nuke
        app = QtWidgets.QApplication.instance()

    PDF = 'PYTHONEDITOR_DEFAULT_FONT'
    os.environ[PDF] = 'Consolas'
    _ide = ide.IDE()
    app.setPalette(nukepalette.getNukePalette())
    _ide.showMaximized()
    plastique = QtWidgets.QStyleFactory.create(
        'Plastique'
    )
    QtWidgets.QApplication.setStyle(plastique)

    print(
        'PythonEditor startup time: %.04f seconds'
        % (time.time()-start)
    )
    sys.exit(app.exec_())
