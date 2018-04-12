from PythonEditor.ui.nukefeatures import nukedock
from PythonEditor.utils import constants
from PythonEditor.ui.Qt import QtWidgets, QtCore, QtGui

panel_name = 'i.d.e.Python_Editor'

reloadAllModules ="""
for m in sys.modules.keys():
    if 'PythonEditor' in m:
        del sys.modules[m]
import PythonEditor
reload(PythonEditor)
from PythonEditor.ui.nukefeatures import nukedock
reload(nukedock)
nukedock.setup_dock()
nukescripts.panels.__panels["i.d.e.Python_Editor"]()
"""

def menu_setup():
    import nuke

    panelMenu = nuke.menu('Nuke').addMenu('Panels')
    panelMenu.addCommand('Python Editor', reloadAllModules,
        '\\', icon=constants.NUKE_DIR + '/icons/PythonEditor.png')

    # #TODO: add command like in ThumbsUp to add to correct panel.
    # nuke.menu('Nodes').addCommand('Python Editor', 
    #     'nukescripts.panels.__panels["i.d.e.Python_Editor"]()', 
    #     'Alt+z', icon=constants.NUKE_DIR + '/icons/PythonEditor.png')

    nuke.menu('Nodes').addCommand('Python Editor', 
        '__import__("PythonEditor").ui.nukefeatures.nukeinit.add_to_pane()',
        'Alt+z', icon=constants.NUKE_DIR + '/icons/PythonEditor.png')

def add_to_pane():
    """
    Locates a panel and adds it to one
    of the main dock windows in order
    of preference.
    """
    panel = None
    for widget in QtWidgets.QApplication.instance().allWidgets():
        if isinstance(widget, QtWidgets.QStackedWidget):
            for child in widget.children():
                if child.objectName() == panel_name:
                    panel = child
                    pane = widget
                    break
    
    if bool(panel):

        pane.setCurrentWidget(panel)
        panel.setFocus(QtCore.Qt.ActiveWindowFocusReason)
        panel.activateWindow()

    else:
        panel = panels.__panels.get(panel_name).__call__()
        for dock in ['Properties.1',
                     'DAG.1',
                     'Viewer.1']:
            pane = nuke.getPaneFor(dock)
            if pane:
                panel.addToPane(pane)
                break

def setup():
    menu_setup()
    nukedock.setup_dock()
