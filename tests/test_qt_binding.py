# test that we can find Qt bindings with Qt.py
# raise ImportError("No Qt binding were found.")

import os
import sys

from PythonEditor.ui.Qt import QtCore, QtGui, QtWidgets
os.environ["QT_VERBOSE"] = "1"

def test_basic_import():
    from PythonEditor.ui.editor import Editor

def test_qt():
    if os.environ.get("QT_PREFERRED_BINDING"):
        if os.environ["QT_PREFERRED_BINDING"].startswith("PySide2"):
            import PySide2
        if os.environ["QT_PREFERRED_BINDING"].startswith("PySide6"):
            import PySide6


def test_editor_drag_enter_event():
    created_app = False
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
        created_app = True

    from PythonEditor.ui import editor as editor_module

    editor = editor_module.Editor(init_features=False)
    mime = QtCore.QMimeData()
    mime.setUrls([QtCore.QUrl.fromLocalFile("C:/tmp/test.txt")])

    pos = QtCore.QPointF(0, 0) if QtCore.qVersion().startswith("6") else QtCore.QPoint(0, 0)
    drag_event = QtGui.QDragEnterEvent(
        pos,
        QtCore.Qt.CopyAction,
        mime,
        QtCore.Qt.LeftButton,
        QtCore.Qt.NoModifier,
    )

    assert editor.event(drag_event) is True

    editor.close()
    QtWidgets.QApplication.processEvents()
    if created_app:
        app.quit()
