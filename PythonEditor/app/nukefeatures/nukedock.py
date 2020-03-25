

def setup_dock(shortcut=None):
    """ Register the PythonEditor interface
    as a Nuke docked panel.
    """
    try:
        import nuke
        from nukescripts import PythonPanel, registerPanel
    except ImportError:
        return

    # register the panel manually, expressly for
    # the purpose of redefining the nested addToPane
    # function to take a pane parameter.
    class Panel(PythonPanel):
        def __init__(self, widget, name, _id):
            PythonPanel.__init__(self, name, _id)
            self.custom_knob = nuke.PyCustom_Knob(
                name, '',
                '__import__("nukescripts").panels.WidgetKnob('+widget+')'
            )
            self.addKnob(self.custom_knob)

    widget = '__import__("PythonEditor.ui.ide", fromlist=["IDE"]).IDE'
    name = 'Python Editor'
    _id = 'Python.Editor'
    def add_panel(pane=None):
        return Panel(widget, name, _id).addToPane(pane=pane)

    menu = nuke.menu('Pane')
    menu.addCommand(name, add_panel, shortcut=shortcut)
    registerPanel(_id, add_panel)
