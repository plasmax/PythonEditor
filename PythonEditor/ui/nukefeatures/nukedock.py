"""
For menu.py usage:
from PythonEditor.ui.features import nukedock
nukedock.setup_dock()
"""
import time
import sys
from PythonEditor.utils.constants import NUKE_DIR

reloadAllModules ="""
for m in sys.modules.keys():
    if 'PythonEditor' in m:
        del sys.modules[m]
import PythonEditor
reload(PythonEditor)
from PythonEditor.ui.nukefeatures import nukedock
nukedock.setup_dock()
nukescripts.panels.__panels["i.d.e.Python_Editor"]()
"""

def setup_dock():
    try:
        import nuke
        from nukescripts import registerWidgetAsPanel
        # from nukescripts.panels import PythonPanel, registerPanel
    except ImportError:
        return

    # def registerWidgetAsPanel( widget, name, id, create = False ):
    #     class Panel( PythonPanel ):

    #         def __init__(self, widget, name, id):
    #             PythonPanel.__init__(self, name, id )
    #             self.customKnob = nuke.PyCustom_Knob( name, 
    #                 "", 
    #                 "__import__('nukescripts').panels.WidgetKnob(" + widget + ")" )
    #             self.addKnob( self.customKnob  )

    #     def addPanel(toPane=True):
    #         panel = Panel( widget, name, id )
    #         if toPane:
    #             return panel.addToPane()
    #         else:
    #             return panel

    #     menu = nuke.menu('Pane')
    #     menu.addCommand( name, addPanel)
    #     registerPanel( id, addPanel )

    #     if ( create ):
    #         return Panel( widget, name, id )
    #     else:
    #         return None
    #     registerWidgetAsPanel( widget, name, id, create = False )

    registerWidgetAsPanel('__import__("PythonEditor").ide.IDE', "Python Editor", 'i.d.e.Python_Editor')

    panelMenu = nuke.menu('Nuke').addMenu('Panels')
    panelMenu.addCommand('Python Editor', reloadAllModules,
        '\\', icon= NUKE_DIR + '/icons/PythonEditor.png')

    nuke.menu('Nodes').addCommand('Python Editor', 
        'nukescripts.panels.__panels["i.d.e.Python_Editor"]()', 
        'Alt+z', icon= NUKE_DIR + '/icons/PythonEditor.png')

if NUKE_DIR in sys.path:
    setup_dock()
