# test that we can find Qt bindings with Qt.py
# raise ImportError("No Qt binding were found.")

import os
os.environ["QT_VERBOSE"] = "1"

def test_basic_import():
    from PythonEditor.ui.editor import Editor

