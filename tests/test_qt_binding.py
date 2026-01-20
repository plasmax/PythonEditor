# test that we can find Qt bindings with Qt.py
# raise ImportError("No Qt binding were found.")

import os
os.environ["QT_VERBOSE"] = "1"

def test_basic_import():
    from PythonEditor.ui.editor import Editor

def test_qt():
    if os.environ.get("QT_PREFERRED_BINDING"):
        if os.environ["QT_PREFERRED_BINDING"].startswith("PySide2"):
            import PySide2
        if os.environ["QT_PREFERRED_BINDING"].startswith("PySide6"):
            import PySide6