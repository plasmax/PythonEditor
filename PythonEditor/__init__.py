import os
from PythonEditor.utils.constants import QT_VERSION
os.environ['QT_PREFERRED_BINDING'] = QT_VERSION

from PythonEditor.ui import ide

def nuke_menu_setup():
    """
    If in Nuke, setup menu.
    """
    try:
        import nuke
    except ImportError:
        return

    from PythonEditor.ui.nukefeatures import nukeinit
    nukeinit.setup()

nuke_menu_setup()
