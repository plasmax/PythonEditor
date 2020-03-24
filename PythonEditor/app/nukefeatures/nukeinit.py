import sys
from os.path import dirname

from PythonEditor.app.nukefeatures import nukedock
from PythonEditor.core import streams
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
RELOAD_CMD = """
# Remove PythonEditor Panel
# ------------------------------------------
from Qt import QtWidgets, QtGui, QtCore

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
for m in sys.modules.keys():
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
dock = nuke.thisPane()
candidates = ['Properties.1', 'Viewer.1',  'DAG.1']

for tab_name in candidates:
    pane = nuke.getPaneFor(tab_name)
    if pane is not None:
        dock = pane # to set order of preference
        break # the current pane was a candidate. done!

nukescripts.panels.__panels["Python.Editor"].__call__(pane=dock)
"""

IMPORT_CMD = '__import__("PythonEditor")'\
    '.app.nukefeatures.nukeinit.add_to_pane()'

ICON_PATH = 'PythonEditor.png'


def setup(nuke_menu=False, node_menu=False, pane_menu=True):
    """
    PythonEditor requires the pane menu to be setup in order to
    be accessible to the user (without launching the panel
    programmatically). The nuke_menu and node_menu exist as optional
    extras.

    TODO:
    Set this up automatically based on Preferences.
    """
    if not IN_NUKE_GUI_MODE:
        return

    if nuke_menu:
        add_nuke_menu()

    if node_menu:
        add_node_menu()

    if pane_menu:
        nukedock.setup_dock()


def add_nuke_menu():
    """
    Adds a "Panels" menu to the Nuke menubar.
    """
    try:
        package_dir = dirname(dirname(sys.modules['PythonEditor'].__file__))
        nuke.pluginAddPath(package_dir)
    except Exception as error:
        print(error)
    panelMenu = nuke.menu('Nuke').addMenu('Panels')
    panelMenu.addCommand('Python Editor',
                         IMPORT_CMD,
                         icon=ICON_PATH)

    panelMenu.addCommand('[dev] Fully Reload Python Editor',
                         RELOAD_CMD,
                         icon=ICON_PATH)


def add_node_menu():
    """
    Adds a menu item to the Node Menu.
    """
    nuke.menu('Nodes').addCommand('Py',
                              IMPORT_CMD,
                              shortcut='\\',
                              icon=ICON_PATH)


def capture_ui_state():
    """
    Get the current workspace layout.
    """
    ui_state = {}
    pythoneditor_panel = None
    for widget in QtWidgets.QApplication.instance().allWidgets():
        if isinstance(widget, QtWidgets.QStackedWidget):
            ui_state[widget] = widget.currentWidget()
    return ui_state


def focus_on_panel(ui_state, panel_name=PANEL_NAME):
    panels = [p for s in ui_state.keys() for p in s.children()]
    for stack in ui_state.keys():
        for child in stack.children():
            if child.objectName() == panel_name:
                pythoneditor_panel = child
                qt_pane = stack
                qt_pane.setCurrentWidget(pythoneditor_panel)
                pythoneditor_panel.setFocus(QtCore.Qt.ActiveWindowFocusReason)
                pythoneditor_panel.activateWindow()
                return True


def add_to_pane():
    """
    Locates a panel and adds it to one
    of the main dock windows in order
    of preference.

    BUG: This now seems to disagree greatly with the "Reload Package"
    feature, causing many segfault.
    """
    ui_state = capture_ui_state()
    if focus_on_panel(ui_state):
        # the Python Editor tab exists, switch to it. (this should ideally be in focus_on_panel)
        for tabbar in QtWidgets.QApplication.instance().allWidgets():
            if isinstance(tabbar, QtWidgets.QTabBar):
                for i in range(tabbar.count()):
                    if tabbar.tabText(i) == 'Python Editor':
                        if tabbar.currentIndex() != i:
                            tabbar.setCurrentIndex(i)
                        break
        return

    import nuke
    from nukescripts import panels
    found = False

    # is the active pane one of the ones we want to add Python Editor to?
    dock = nuke.thisPane()
    candidates = ['Properties.1', 'Viewer.1',  'DAG.1']

    for tab_name in candidates:
        pane = nuke.getPaneFor(tab_name)
        if pane is not None:
            dock = pane # to set order of preference
            break # the current pane was a candidate. done!

    # this will create the PythonEditor panel and add it to the active pane
    nuke_panel = panels.__panels.get(PANEL_NAME).__call__(pane=dock)
