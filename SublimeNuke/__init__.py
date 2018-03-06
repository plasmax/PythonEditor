import time
print 'importing', __name__, 'at', time.asctime()

import IDE
reload(IDE)


LEVEL_ONE = True

if __name__ != '__main__':
    import nukescripts
    cmd = 'lambda g=globals(), l=locals(): __import__("SublimeNuke").IDE.IDE(g, l)'
    nukescripts.registerWidgetAsPanel(cmd, "IDE", 'i.d.e')
    import nuke
    nuke.menu('Nuke').addCommand('Sublime Nuke', 
        'import SublimeNuke;reload(SublimeNuke);'\
        'nukescripts.panels.__panels["i.d.e"]()', 
        '\\', icon='C:/Users/Max-Last/.nuke/icons/SublimeNuke.png')
