import sys
from os.path import dirname

from PythonEditor.app.nukefeatures import nukedock
from PythonEditor.utils import constants
from PythonEditor.ui.Qt import QtWidgets, QtCore

try:
    import nuke
    IN_NUKE_GUI_MODE = nuke.GUI
except ImportError:
    IN_NUKE_GUI_MODE = False


PANEL_NAME = 'Python.Editor'

"""
The purpose of this command is to fully re-initiliase the
PythonEditor module for two purposes:
1) to speed up development
2) to act as a "repair" command in the event PythonEditor
stops working.

# TODO: could this be in a function? Do I want it to be?
Also, this should close the Python Editor before reloading/restoring
"""

# FIXME: iterating through allWidgets is bad practice and causes 
# PySide objects to go out of scope.
RELOAD_CMD = """
# Remove PythonEditor Panel
# ------------------------------------------
from PythonEditor.ui.Qt import QtWidgets, QtGui, QtCore

def remove_panel(PANEL_NAME):
    for stack in QtWidgets.QApplication.instance().allWidgets():
        if not isinstance(stack, QtWidgets.QStackedWidget):
            continue
        for child in stack.children():
            if child.objectName() == PANEL_NAME:
                child.deleteLater()

remove_panel('Python.Editor')

# Reset standard and error outputs
# ------------------------------------------
try:
    sys.stdout.reset()
    sys.stderr.reset()
except Exception as e:
    print(e)

# Remove all Python Editor modules
# ------------------------------------------
for m in list(sys.modules.keys()):
    if 'PythonEditor' in m:
        del sys.modules[m]

# Reload main module
# ------------------------------------------
import PythonEditor
reload(PythonEditor)

# Rerun menu setup
# ------------------------------------------
from PythonEditor.app.nukefeatures import nukedock
reload(nukedock)
nukedock.setup_dock()

from PythonEditor.app.nukefeatures import nukeinit
reload(nukeinit)

# Re-launch panel
# ------------------------------------------
PythonEditor.app.nukefeatures.nukeinit.add_to_pane()
"""

IMPORT_CMD = (
    '__import__("PythonEditor")'
    '.app.nukefeatures.nukeinit.add_to_pane()'
)

ICON_PATH = 'PythonEditor.png'


def setup(nuke_menu=False, node_menu=False, pane_menu=True, shortcut='\\'):
    """PythonEditor requires the pane menu to be setup in order to
    be accessible to the user (without launching the panel
    programmatically). The nuke_menu and node_menu exist as optional
    extras.

    TODO:
    Set this up automatically based on Preferences.
    """
    if not IN_NUKE_GUI_MODE:
        return

    if nuke_menu:
        add_nuke_menu(shortcut=shortcut)

    if node_menu:
        add_node_menu()

    if pane_menu:
        nukedock.setup_dock()


def add_nuke_menu(shortcut='\\'):
    """Adds a "Panels" menu to the Nuke menubar.
    """
    try:
        package_dir = dirname(dirname(sys.modules['PythonEditor'].__file__))
        nuke.pluginAddPath(package_dir)
    except Exception as error:
        print(error)

    nuke_menu = nuke.menu('Nuke')
    panel_menu = nuke_menu.addMenu('Panels')
    panel_menu.addCommand(
        'Python Editor',
        IMPORT_CMD,
        icon=ICON_PATH,
        shortcut=shortcut
    )

    panel_menu.addCommand(
        '[dev] Fully Reload Python Editor',
        RELOAD_CMD,
        icon=ICON_PATH
    )


def add_node_menu():
    """Adds a menu item to the Node Menu.
    """
    node_menu = nuke.menu('Nodes')
    node_menu.addCommand(
        'Py',
        IMPORT_CMD,
        icon=ICON_PATH
    )


def add_to_pane():
    """Add or move PythonEditor to the current or default pane. Only
    one instance of the PythonEditor widget is allowed at a time.

    BUG: This now seems to disagree greatly with the "Reload Package"
    feature, causing many a segfault.
    """
    # nuke-specific imports in here so that PythonEditor works outside of nuke.
    import nuke
    from nukescripts.panels import __panels

    # is the active pane one of the ones we want to add Python Editor to?
    candidates = ['Viewer.1', 'Properties.1', 'DAG.1']

    for tab_name in candidates:
        dock = nuke.getPaneFor(tab_name)
        if dock is None:
            continue
        break
    else:
        # no "break"? use thisPane
        dock = nuke.thisPane()

    import PythonEditor
    try:
        # if the panel exists already, it's 
        # likely the user is trying to move it.
        ide = PythonEditor.__dock
        ide.addToPane(dock)
    except AttributeError:
        nuke_panel = __panels.get(PANEL_NAME).__call__(pane=dock)

