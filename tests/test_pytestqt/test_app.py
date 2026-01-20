import os
import sys

import pytest

from PythonEditor.ui import ide
from PythonEditor.ui.features import nukepalette
from PythonEditor.ui.Qt import QtWidgets, QtGui


@pytest.mark.gui
def test_app_launch():
    # add the package path to sys.path
    folder = os.path.dirname(__file__)
    package_path = os.path.dirname(folder)
    if package_path not in sys.path:
        sys.path.append(package_path)

    created_app = False
    try:
        app = QtWidgets.QApplication(sys.argv)
        created_app = True
    except RuntimeError:
        # for running inside and outside of other applications
        app = QtWidgets.QApplication.instance()

    # set the application icon
    icon_path = os.path.join(package_path, 'icons', 'PythonEditor.png')
    icon = QtGui.QIcon(icon_path)
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

    editor = ide.IDE()
    editor.show()
    QtWidgets.QApplication.processEvents()
    if created_app:
        app.quit()
    assert editor.isVisible()
    editor.close()
    QtWidgets.QApplication.processEvents()

