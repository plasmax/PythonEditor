""" PythonEditor by Max Last.

The object hierarchy is:
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
    """The main entrypoint into PythonEditor.
    Makes sure the environment is configured correctly for Qt.py.
    """

    # Because we are using Qt.py, we actually don't need to
    # specify our preferred bindings; it's latest-first.
    # However, Nuke 10 crashes if you try and import PySide2,
    # so in that case we will hardcode a preference.
    try:
        import nuke
        if nuke.NUKE_VERSION_MAJOR < 11:
            import os
            if not os.environ.get('QT_PREFERRED_BINDING'):
                os.environ['QT_PREFERRED_BINDING'] = 'PySide'
    except ImportError:
        pass

    # do not create .pyc files
    import sys
    sys.dont_write_bytecode = True

    try:
        from PythonEditor.ui.features.actions import backup_pythoneditor_history
        backup_pythoneditor_history(in_tmp=True)
    except Exception:
        pass


def _print_load_error(error):
    import traceback
    print('Sorry! There has been an error loading PythonEditor:')
    traceback.print_exc()
    print(error)
    print('Please contact tsalxam@gmail.com with the above error details.')


def nuke_menu_setup(nuke_menu=False, node_menu=False, pane_menu=True):
    """ If in Nuke, set up menu.

    :param nuke_menu: `bool` Add menu items to the main Nuke menu.
    :param node_menu: `bool` Add menu item to the Node menu.
    :param pane_menu: `bool` Add menu item to the Pane menu.
    """
    try:
        import nuke
    except ImportError:
        return

    try:
        from PythonEditor.app.nukefeatures import nukeinit
        nukeinit.setup(nuke_menu=nuke_menu, node_menu=node_menu, pane_menu=pane_menu)
    except Exception as e:
        _print_load_error(e)


try:
    main()
except Exception as e:
    _print_load_error(e)
