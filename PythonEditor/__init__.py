import os
# anti-crash prevention from Nuke 11 to 10.
bindings = 'PySide2', 'PyQt5', 'PySide', 'PyQt4'
os.environ['QT_PREFERRED_BINDING'] = os.pathsep.join(bindings)

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
