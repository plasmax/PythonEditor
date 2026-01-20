# test that we can find Qt bindings with Qt.py
# raise ImportError("No Qt binding were found.")

import os
import sys
import warnings

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

    # PySide6 QDragEnterEvent expects QPoint (not QPointF) for the position.
    pos = QtCore.QPoint(0, 0)
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
def test_launch_steps_subprocess_syntax_highlighter_regexp():
    created_app = False
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
        created_app = True

    from PythonEditor.ui import editor as editor_module
    from PythonEditor.ui.features import syntaxhighlighter

    editor = editor_module.Editor(init_features=False)
    highlighter = syntaxhighlighter.Highlight(editor.document(), editor)
    editor.setPlainText("class Foo:\n    def bar(self):\n        return 1\n")
    highlighter.rehighlight()

    editor.close()
    QtWidgets.QApplication.processEvents()
    if created_app:
        app.quit()


@pytest.mark.gui
def test_launch_steps_subprocess_shortcut_event_filter():
    created_app = False
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
        created_app = True

    from PythonEditor.ui import editor as editor_module
    from PythonEditor.ui.features import shortcuts

    editor = editor_module.Editor(init_features=False)
    handler = shortcuts.ShortcutHandler(editor=editor)
    paint_event = QtGui.QPaintEvent(QtCore.QRect(0, 0, 1, 1))
    assert handler.eventFilter(editor, paint_event) is False

    editor.close()
    QtWidgets.QApplication.processEvents()
    if created_app:
        app.quit()


@pytest.mark.gui
def test_shortcut_handler_tab_after_dot():
    created_app = False
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
        created_app = True

    from PythonEditor.ui import editor as editor_module
    from PythonEditor.ui.features import actions, shortcuts

    editor = editor_module.Editor(init_features=False)
    actions.Actions(editor=editor)
    handler = shortcuts.ShortcutHandler(editor=editor)
    key_event = QtGui.QKeyEvent(
        QtCore.QEvent.KeyPress,
        QtCore.Qt.Key_Tab,
        QtCore.Qt.NoModifier,
        "\t",
    )

    editor.setPlainText("import os\nos. ")
    cursor = editor.textCursor()
    cursor.movePosition(QtGui.QTextCursor.End)
    cursor.movePosition(QtGui.QTextCursor.Left)
    editor.setTextCursor(cursor)
    assert handler.handle_keypress(key_event) is False

    editor.setPlainText("import os\nos. ")
    cursor = editor.textCursor()
    cursor.movePosition(QtGui.QTextCursor.End)
    editor.setTextCursor(cursor)
    assert handler.handle_keypress(key_event) is True

    editor.close()
    QtWidgets.QApplication.processEvents()
    if created_app:
        app.quit()


@pytest.mark.gui
def test_autocomplete_tab_after_dot_with_trailing_space():
    created_app = False
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
        created_app = True

    from PythonEditor.ui import editor as editor_module
    from PythonEditor.ui.features import autocompletion

    editor = editor_module.Editor(init_features=False)
    completer = autocompletion.AutoCompleter(editor)
    editor.autocomplete_overriding = True

    editor.setPlainText("import os\nos. ")
    cursor = editor.textCursor()
    cursor.movePosition(QtGui.QTextCursor.End)
    cursor.movePosition(QtGui.QTextCursor.Left)
    editor.setTextCursor(cursor)

    key_event = QtGui.QKeyEvent(
        QtCore.QEvent.KeyPress,
        QtCore.Qt.Key_Tab,
        QtCore.Qt.NoModifier,
        "\t",
    )
    assert completer._pre_keyPressEvent(key_event) is True

    editor.close()
    QtWidgets.QApplication.processEvents()
    if created_app:
        app.quit()


@pytest.mark.gui
def test_terminal_line_from_event_block_under_cursor():
    created_app = False
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
        created_app = True

    from PythonEditor.ui import terminal as terminal_module

    terminal = terminal_module.Terminal()
    terminal.setPlainText("first line\nsecond line")

    class DummyEvent(object):
        def __init__(self, pos):
            self._pos = pos

        def pos(self):
            return self._pos

    line = terminal.line_from_event(DummyEvent(QtCore.QPoint(1, 1)))
    assert line == "first line"

    terminal.stop()
    terminal.close()
    QtWidgets.QApplication.processEvents()
    if created_app:
        app.quit()


@pytest.mark.gui
def test_qt_exec_compat_no_deprecation_warning():
    created_app = False
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
        created_app = True

    from PythonEditor.utils import qt_compat

    QtCore.QTimer.singleShot(0, app.quit)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", DeprecationWarning)
        qt_compat.exec_app(app)

    assert not any(
        isinstance(warning.message, DeprecationWarning)
        for warning in caught
    )

    if created_app:
        app.quit()


@pytest.mark.gui
def test_shortcuts_key_to_sequence_with_modifier(monkeypatch):
    created_app = False
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
        created_app = True

    from PythonEditor.ui.features import shortcuts

    class DummyApp(object):
        @staticmethod
        def keyboardModifiers():
            return QtCore.Qt.ControlModifier

    monkeypatch.setattr(shortcuts, "QApplication", DummyApp)
    seq = shortcuts.key_to_sequence(QtCore.Qt.Key_T)
    assert seq.toString()

    if created_app:
        app.quit()


@pytest.mark.gui
def test_shortcuts_key_to_sequence_with_modifier_int_key(monkeypatch):
    created_app = False
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
        created_app = True

    from PythonEditor.ui.features import shortcuts

    class DummyApp(object):
        @staticmethod
        def keyboardModifiers():
            return QtCore.Qt.ControlModifier

    monkeypatch.setattr(shortcuts, "QApplication", DummyApp)
    seq = shortcuts.key_to_sequence(int(QtCore.Qt.Key_T))
    assert seq.toString()

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
