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
    import os
    bindings = 'PySide2', 'PyQt5', 'PySide', 'PyQt4'

    # anti-crash prevention from Nuke 11 to 10.
    try:
        import nuke
        pyside = ('PySide' if (nuke.NUKE_VERSION_MAJOR < 11) else 'PySide2')
    except ImportError:
        pyside = 'PySide'

    if not os.environ.get('QT_PREFERRED_BINDING'):
        os.environ['QT_PREFERRED_BINDING'] = pyside
        # this seems to not cause any crashes either
        'PySide2:PySide:PyQt5:PyQt4'

    global ide
    from PythonEditor.ui import ide

    # for convenience - FIXME: this
    # should be developer-only or at least
    # disableable
    import sys

    # do not create .pyc files
    sys.dont_write_bytecode = True

    from ui import Qt

    # enable "from Qt import x" and
    sys.modules['Qt'] = Qt

    # enable "from Qt.QtCore import *"
    for name in Qt.__all__:
        sys.modules['Qt.{0}'.format(name)] = vars(Qt)[name]


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
