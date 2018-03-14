__panels = {}

class PythonPanel():
    def __init__(self, name, id ):
        print name, id

    def addKnob(self, knob):
        print knob

    def addToPane(self, pane=None):
        pass

def registerPanel( id, func ):
    __panels[id] = func

class WidgetKnob():
    def __init__(self, widgetString ):
        print widgetString