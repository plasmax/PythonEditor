"""
PythonEditor by Max Last.

The package loading structure is as follows:
ide ->
    pythoneditor ->
        tabs ->
            terminal
            editor
        menubar ->
            dialogs
"""

import os
# anti-crash prevention from Nuke 11 to 10.
bindings = 'PySide2', 'PyQt5', 'PySide', 'PyQt4'

try:
    import nuke
    pyside = ('PySide' if (nuke.NUKE_VERSION_MAJOR < 11) else 'PySide2')
except ImportError:
    pyside = 'PySide'

if not os.environ.get('QT_PREFERRED_BINDING'):
    os.environ['QT_PREFERRED_BINDING'] = pyside

from PythonEditor.ui import ide

# for convenience
from ui import Qt
import sys
sys.modules['Qt'] = Qt


def nuke_menu_setup(nuke_menu=False, node_menu=False, pane_menu=True):
    """
    If in Nuke, setup menu.
    """
    try:
        import nuke
    except ImportError:
        return

    from PythonEditor.ui.nukefeatures import nukeinit
    nukeinit.setup(nuke_menu=nuke_menu, node_menu=node_menu, pane_menu=pane_menu)

