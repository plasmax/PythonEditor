

def setup_dock(shortcut=None):
    """Register the PythonEditor interface
    as a Nuke docked panel.
    """
    import nuke
    from nukescripts import PythonPanel, registerPanel

    # register the panel manually, expressly for
    # the purpose of redefining the nested addToPane
    # function to take a pane parameter.
    class Panel(PythonPanel):
        # This class was previously nested within
        # the nukescripts.registerWidgetAsPanel function.
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
        """Add or move existing PythonEditor
        panel to a new pane. This is what
        makes the PythonEditor a singleton.
        
        :param pane: Nuke <type 'Dock'>

        TODO: maybe not here, but this should trigger the "in focus" signal that overrides shortcuts
        """
        import PythonEditor
        try:
            panel = PythonEditor.__dock
        except AttributeError:
            panel = Panel(widget, name, _id)
            PythonEditor.__dock = panel
        return panel.addToPane(pane=pane)

    menu = nuke.menu('Pane')
    menu.addCommand(name, add_panel, shortcut=shortcut)
    registerPanel(_id, add_panel)
