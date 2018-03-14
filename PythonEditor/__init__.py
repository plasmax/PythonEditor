import os
import time
import sys
print 'importing', __name__, 'at', time.asctime()
user = os.environ.get('USERNAME')


reloadAllModules ="""
for m in sys.modules.keys():
    if 'PythonEditor' in m:
        del sys.modules[m]
import PythonEditor
reload(PythonEditor)
nukescripts.panels.__panels["i.d.e"]()
"""

from constants import NUKE_DIR

def main():
    import IDE

    try:
        import nuke
        from nukescripts.panels import PythonPanel, registerPanel
    except ImportError:
        pass

    def registerWidgetAsPanel( widget, name, id, create = False ):
        class Panel( PythonPanel ):

            def __init__(self, widget, name, id):
                PythonPanel.__init__(self, name, id )
                self.customKnob = nuke.PyCustom_Knob( name, 
                    "", 
                    "__import__('nukescripts').panels.WidgetKnob(" + widget + ")" )
                self.addKnob( self.customKnob  )

        def addPanel(toPane=True):
            panel = Panel( widget, name, id )
            if toPane:
                return panel.addToPane()
            else:
                return panel

        menu = nuke.menu('Pane')
        menu.addCommand( name, addPanel)
        registerPanel( id, addPanel )

        if ( create ):
            return Panel( widget, name, id )
        else:
            return None
        registerWidgetAsPanel( widget, name, id, create = False )

    registerWidgetAsPanel('__import__("PythonEditor").IDE.IDE', "Python Editor", 'i.d.e')

    nuke.menu('Nuke').addCommand('.   Python Editor   .', reloadAllModules,
        '\\', icon= NUKE_DIR + '/icons/PythonEditor.png')

    nuke.menu('Nodes').addCommand('Python Editor', 
        'nukescripts.panels.__panels["i.d.e"](toPane=False).show()', 
        'Alt+z', icon= NUKE_DIR + '/icons/PythonEditor.png')

if NUKE_DIR in sys.path:
    main()
