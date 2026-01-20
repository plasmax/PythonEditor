# test that we can find Qt bindings with Qt.py
# raise ImportError("No Qt binding were found.")

import os
import sys

import pytest

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


@pytest.mark.gui
def test_ide_smoke_event_loop():
    created_app = False
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
        created_app = True

    from PythonEditor.ui import ide

    editor = ide.IDE()
    editor.showMaximized()

    QtCore.QTimer.singleShot(200, editor.close)
    QtCore.QTimer.singleShot(250, app.quit)
    app.exec_()

    QtWidgets.QApplication.processEvents()
    if created_app:
        app.quit()


@pytest.mark.gui
def test_launch_steps_subprocess():
    import subprocess

    steps = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    for step in steps:
        duration_args = []
        if step in (2, 3, 4, 5, 6, 7, 8):
            duration_args = ["--duration-ms", "1000"]
        result = subprocess.run(
            [sys.executable, "-m", "tests.diagnostics.launch_steps", "--step", str(step)]
            + duration_args,
            capture_output=True,
            text=True,
            env=os.environ.copy(),
            timeout=10,
        )
        assert result.returncode == 0, (
            f"launch step {step} failed with {result.returncode}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
