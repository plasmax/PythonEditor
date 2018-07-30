import os
# anti-crash prevention from Nuke 11 to 10.
os.environ['QT_PREFERRED_BINDING'] = 'PySide2:PySide:PyQt5:PyQt4'


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
