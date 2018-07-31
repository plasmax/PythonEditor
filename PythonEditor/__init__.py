import os
# anti-crash prevention from Nuke 11 to 10.

try:
    import nuke
    pyside = ('PySide' if (nuke.NUKE_VERSION_MAJOR < 11) else 'PySide2')
except ImportError:
    pyside = 'PySide'

os.environ['QT_PREFERRED_BINDING'] = pyside

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
