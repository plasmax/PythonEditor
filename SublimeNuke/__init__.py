import os
import time
print 'importing', __name__, 'at', time.asctime()
user = os.environ.get('USERNAME')

import IDE
# reload(IDE)

try:
    import nuke
    from nukescripts.panels import PythonPanel, registerPanel
except ImportError:
    pass

def registerWidgetAsPanel( widget, name, id, create = False ):
    class Panel( PythonPanel ):

        def __init__(self, widget, name, id):
            PythonPanel.__init__(self, name, id )
            self.customKnob = nuke.PyCustom_Knob( name, "", "__import__('nukescripts').panels.WidgetKnob(" + widget + ")" )
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

LEVEL_ONE = True
reloadcmd = "for m in sys.modules.keys():\n" \
                "\tif 'Sublime' in m:\n"\
                "\t\tdel sys.modules[m]"

reloadAllModules ="""
for m in sys.modules.keys():
    if 'Sublime' in m:
        del sys.modules[m]
import SublimeNuke
reload(SublimeNuke)
nukescripts.panels.__panels["i.d.e"]()
"""

if __name__ != '__main__':
    registerWidgetAsPanel('__import__("SublimeNuke").IDE.IDE', "IDE", 'i.d.e')

    nuke.menu('Nuke').addCommand('Sublime Nuke', reloadAllModules,
        '\\', icon='C:/Users/{}/.nuke/icons/SublimeNuke.png'.format(user))

    nuke.menu('Nodes').addCommand('Sublime Nuke', 
        'nukescripts.panels.__panels["i.d.e"](toPane=False).show()', 
        'Alt+z', icon='C:/Users/{}/.nuke/icons/SublimeNuke.png'.format(user))
    
