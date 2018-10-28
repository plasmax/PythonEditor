from PythonEditor.ui.nukefeatures import nukedock
from PythonEditor.ui.nukefeatures import scripteditorshortcuts
from PythonEditor.utils import constants
from PythonEditor.ui.Qt import QtWidgets, QtCore

PANEL_NAME = 'i.d.e.Python_Editor'

RELOAD_CMD = """
for m in sys.modules.keys():
    if 'PythonEditor' in m:
        del sys.modules[m]
import PythonEditor
reload(PythonEditor)
from PythonEditor.ui.nukefeatures import nukedock
reload(nukedock)
nukedock.setup_dock()
nukescripts.panels.__panels["i.d.e.Python_Editor"]()
from PythonEditor.ui.nukefeatures import nukeinit
reload(nukeinit)
"""

ICON_PATH = 'PythonEditor.png'


def setup(nuke_menu=False, node_menu=False, pane_menu=True):
    """
    TODO:
    Set this up automatically based on Preferences.
    """
    try:
        import nuke
        if not nuke.GUI:
            return
    except ImportError:
        pass

    import_cmd = '__import__("PythonEditor")'\
        '.ui.nukefeatures.nukeinit.add_to_pane()'

    if nuke_menu:
        panelMenu = nuke.menu('Nuke').addMenu('Panels')
        panelMenu.addCommand('Python Editor',
                             import_cmd,
                             icon=ICON_PATH)

        panelMenu.addCommand('Fully Reload Python Editor',
                             RELOAD_CMD,
                             icon=ICON_PATH)

    if node_menu:
        nuke.menu('Nodes').addCommand('Python Editor',
                                      import_cmd,
                                      shortcut='\\',
                                      icon=ICON_PATH)

    if pane_menu:
        nukedock.setup_dock()


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
    """
    ui_state = capture_ui_state()
    if focus_on_panel(ui_state):
        return

    import nuke
    from nukescripts import panels
    found = False

    # this will create the PythonEditor panel and add it to the active pane
    nuke_panel = panels.__panels.get(PANEL_NAME).__call__()

    # reset Nuke ui to how it was.
    for stack, widget in ui_state.items():
        stack.setCurrentWidget(widget)

    for dock in ['Properties.1',
                 'Viewer.1',  'DAG.1']:
        pane = nuke.getPaneFor(dock)
        if pane is not None:
            nuke_panel.addToPane(pane)
            break

    focus_on_panel(capture_ui_state())
    for tabbar in QtWidgets.QApplication.instance().allWidgets():
        if isinstance(tabbar, QtWidgets.QTabBar):
            for i in range(tabbar.count()):
                if tabbar.tabText(i) == 'Python Editor':
                    tabbar.setCurrentIndex(i)
