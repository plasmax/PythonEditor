# AGENTS

This repo already has Qt binding coverage. Avoid opening heavy files unless needed. Make sure to update AGENTS.md if you discover time-saving information for the next agent working on this codebase.

## Quick context
- Bug reproduced by `tests/test_qt_binding.py::test_shortcut_handler_tab_after_dot`.
- The failure was `cursor.LineUnderCursor` on PySide6 (not present on instance).
- Fix is in `PythonEditor/ui/features/shortcuts.py` by selecting via `QTextCursor.LineUnderCursor` or `QTextCursor.SelectionType.LineUnderCursor`.

## Fast grep paths
- Shortcuts: `PythonEditor/ui/features/shortcuts.py`
- Editor init: `PythonEditor/ui/editor.py`
- Qt binding tests: `tests/test_qt_binding.py`

## Avoid
- `PythonEditor/ui/Qt.py` is huge; only open if you must change binding behavior.

## Test commands
- PySide6: `\.venv\Scripts\activate; $env:QT_PREFERRED_BINDING="PySide6"; pytest -vv`
- PySide2: `\.venv\Scripts\activate; $env:QT_PREFERRED_BINDING="PySide2"; pytest -vv`
