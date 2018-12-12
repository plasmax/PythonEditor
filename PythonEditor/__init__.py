"""
PythonEditor by Max Last.

The object Hierarchy is:
IDE
    PythonEditor
        TabEditor
            Tabs
            Editor
                AutoCompleter
                AutoSaveManager
                LineNumberArea
                ShortcutHandler
                Highlight
        Terminal
        MenuBar
        ObjectInspector
        PreferencesEditor
        ShortcutEditor
        Actions
"""

def main():
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

    global ide
    from PythonEditor.ui import ide

    # for convenience
    global Qt
    from ui import Qt
    import sys
    sys.modules['Qt'] = Qt


def nuke_menu_setup(nuke_menu=False, node_menu=False, pane_menu=True):
    """
    If in Nuke, setup menu.

    :param nuke_menu: Add menu items to the main Nuke menu.
    :param node_menu: Add menu item to the Node menu.
    :param pane_menu: Add menu item to the Pane menu.
    """
    try:
        import nuke
    except ImportError:
        return

    try:
        from PythonEditor.ui.nukefeatures import nukeinit
        nukeinit.setup(nuke_menu=nuke_menu, node_menu=node_menu, pane_menu=pane_menu)
    except Exception as e:
        msg = """
        Sorry! There has been an error loading PythonEditor:
        {0}
        Please contact tsalxam@gmail.com with the error details.
        """.format(e)
        print(msg)

try:
    main()
except Exception as e:
    msg = """
    Sorry! There has been an error loading PythonEditor:
    {0}
    Please contact tsalxam@gmail.com with the error details.
    """.format(e)
    print(msg)
