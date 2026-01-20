# BUG

## Autocomplete fails when space precedes dot

### Repro
1) Launch with PySide6 (or PySide2) and open the editor.
2) Ensure a live variable exists, e.g. type and execute: `import os`.
3) On a new line, type: `os .` (note the space before the dot).
4) Place the cursor immediately to the right of the dot.
5) Press Tab.

### Expected
Autocomplete popup should appear for the object (same as `os.` without the space).

### Actual
No completion options are shown.

### Notes
- Recent fixes allow Tab-after-dot with trailing spaces (e.g. `os. `) and prevent literal tab insertion.
- The issue seems specific to a space *before* the dot (i.e. `os .`).
- Likely related code paths:
  - `PythonEditor/ui/features/autocompletion.py` in `_pre_keyPressEvent` (Tab handling) and `complete_object`.
  - `PythonEditor/ui/features/shortcuts.py` (Tab key routing).


##

Error in PySide6 version when clicking between tabs

Traceback (most recent call last):
  File "I:\dev\PythonEditor\PythonEditor\ui\tabs.py", line 893, in set_editor_contents
    self.editor.moveCursor(cursor.End)
AttributeError: 'PySide6.QtGui.QTextCursor' object has no attribute 'End'