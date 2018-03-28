import nukedock
from PythonEditor.utils.constants import NUKE_DIR

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
        '\\', icon= NUKE_DIR + '/icons/PythonEditor.png')

    #TODO: add command like in ThumbsUp to add to correct panel.
    nuke.menu('Nodes').addCommand('Python Editor', 
        'nukescripts.panels.__panels["i.d.e.Python_Editor"]()', 
        'Alt+z', icon= NUKE_DIR + '/icons/PythonEditor.png')

def setup():
    menu_setup()
    nukedock.setup_dock()
