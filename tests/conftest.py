import os

# Qt.py prefers PySide6 by default; force PySide2 for tests to match app usage.
os.environ["QT_PREFERRED_BINDING"] = "PySide2"
