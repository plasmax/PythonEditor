import os
import sys

from pytestqt import qtbot
from pytestqt.qt_compat import qt_api

from PythonEditor.ui import ide
from PythonEditor.ui.features import nukepalette
from PythonEditor.ui.Qt import QtWidgets, QtGui


def test_app(qtbot):
    app = qt_api.QApplication.instance()

    # add the package path to sys.path
    FOLDER = os.path.dirname(__file__)
    PACKAGE_PATH = os.path.dirname(FOLDER)

    # set the application icon
    ICON_PATH = os.path.join(PACKAGE_PATH, 'icons', 'PythonEditor.png')
    icon = QtGui.QIcon(ICON_PATH)
    app.setWindowIcon(icon)

    # set style (makes palette work on linux)
    # Plastique isn't available on Windows, so try multiple styles.
    styles = QtWidgets.QStyleFactory.keys()
    for style_name in ['Plastique', 'Fusion']:
        if style_name not in styles:
            continue
        print('Setting style to:', style_name)
        style = QtWidgets.QStyleFactory.create(style_name)
        QtWidgets.QApplication.setStyle(style)
        break

    app.setPalette(nukepalette.getNukePalette())

    _ide = ide.IDE()

