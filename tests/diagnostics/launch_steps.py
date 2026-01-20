import argparse
import os
import sys

from PythonEditor.ui import ide
from PythonEditor.ui.features import nukepalette
from PythonEditor.ui.Qt import QtWidgets, QtGui, QtCore
from PythonEditor.ui import pythoneditor as pythoneditor_module
from PythonEditor.ui import tabs as tabs_module
from PythonEditor.ui import editor as editor_module


def _ensure_app():
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    return app


def _apply_style(app):
    styles = QtWidgets.QStyleFactory.keys()
    for style_name in ["Plastique", "Fusion"]:
        if style_name not in styles:
            continue
        style = QtWidgets.QStyleFactory.create(style_name)
        QtWidgets.QApplication.setStyle(style)
        break
    app.setPalette(nukepalette.getNukePalette())


def step_0():
    app = _ensure_app()
    QtCore.QTimer.singleShot(100, app.quit)
    return app.exec_()


def step_1():
    app = _ensure_app()
    package_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    icon_path = os.path.join(package_path, "icons", "PythonEditor.png")
    icon = QtGui.QIcon(icon_path)
    app.setWindowIcon(icon)
    _apply_style(app)
    QtCore.QTimer.singleShot(100, app.quit)
    return app.exec_()


def step_2(duration_ms):
    app = _ensure_app()
    _apply_style(app)
    _ide = ide.IDE()
    QtCore.QTimer.singleShot(duration_ms, _ide.close)
    QtCore.QTimer.singleShot(duration_ms + 50, app.quit)
    _ide.show()
    return app.exec_()


def step_3(duration_ms):
    app = _ensure_app()
    _apply_style(app)
    _ide = ide.IDE()
    QtCore.QTimer.singleShot(duration_ms, _ide.close)
    QtCore.QTimer.singleShot(duration_ms + 50, app.quit)
    _ide.showMaximized()
    return app.exec_()


def step_4(duration_ms):
    app = _ensure_app()
    package_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    icon_path = os.path.join(package_path, "icons", "PythonEditor.png")
    icon = QtGui.QIcon(icon_path)
    app.setWindowIcon(icon)
    _apply_style(app)

    _ide = ide.IDE()
    QtCore.QTimer.singleShot(duration_ms, _ide.close)
    QtCore.QTimer.singleShot(duration_ms + 50, app.quit)
    _ide.showMaximized()
    return app.exec_()


def step_5(duration_ms):
    app = _ensure_app()
    _apply_style(app)
    widget = editor_module.Editor(init_features=True)
    QtCore.QTimer.singleShot(duration_ms, widget.close)
    QtCore.QTimer.singleShot(duration_ms + 50, app.quit)
    widget.show()
    return app.exec_()


def step_6(duration_ms):
    app = _ensure_app()
    _apply_style(app)
    widget = editor_module.Editor(init_features=False)
    QtCore.QTimer.singleShot(duration_ms, widget.close)
    QtCore.QTimer.singleShot(duration_ms + 50, app.quit)
    widget.show()
    return app.exec_()


def step_7(duration_ms):
    app = _ensure_app()
    _apply_style(app)
    tab_editor = tabs_module.TabEditor(None)
    QtCore.QTimer.singleShot(duration_ms, tab_editor.close)
    QtCore.QTimer.singleShot(duration_ms + 50, app.quit)
    tab_editor.show()
    return app.exec_()


def step_8(duration_ms):
    app = _ensure_app()
    _apply_style(app)
    pe = pythoneditor_module.PythonEditor(None)
    QtCore.QTimer.singleShot(duration_ms, pe.close)
    QtCore.QTimer.singleShot(duration_ms + 50, app.quit)
    pe.show()
    return app.exec_()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--step", type=int, required=True)
    parser.add_argument("--duration-ms", type=int, default=200)
    args = parser.parse_args()

    steps = {
        0: step_0,
        1: step_1,
        2: step_2,
        3: step_3,
        4: step_4,
        5: step_5,
        6: step_6,
        7: step_7,
        8: step_8,
    }
    if args.step not in steps:
        raise SystemExit(f"Unknown step: {args.step}")
    if args.step in (2, 3, 4, 5, 6, 7, 8):
        return steps[args.step](args.duration_ms)
    return steps[args.step]()


if __name__ == "__main__":
    raise SystemExit(main())
