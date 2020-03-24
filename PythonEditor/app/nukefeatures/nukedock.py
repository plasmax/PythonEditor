

def setup_dock():
    try:
        import nukescripts
    except ImportError:
        return

    globals().update(**nukescripts.__dict__) # basically from nukescripts import *

    def registerWidgetAsPanel ( widget, name, id, create = False ):
      """registerWidgetAsPanel(widget, name, id, create) -> PythonPanel

        Wraps and registers a widget to be used in a Nuke panel.

        widget - should be a string of the class for the widget
        name - is is the name as it will appear on the Pane menu
        id - should the the unique ID for this widget panel
        create - if this is set to true a new NukePanel will be returned that wraps this widget

        Example ( using PyQt )

        import nuke
        import PyQt4.QtCore as QtCore
        import PyQt4.QtGui as QtGui
        from nukescripts import panels

        class NukeTestWindow(QtGui.QWidget):
          def __init__(self, parent=None):
            QtGui.QWidget.__init__(self, parent)
            self.setLayout( QtGui.QVBoxLayout() )
            self.myTable    = QtGui.QTableWidget( )
            self.myTable.header = ['Date', 'Files', 'Size', 'Path' ]
            self.myTable.size = [ 75, 375, 85, 600 ]
            self.layout().addWidget( self.myTable )

        nukescripts.registerWidgetAsPanel('NukeTestWindow', 'NukeTestWindow', 'uk.co.thefoundry.NukeTestWindow' )

      """

      class Panel( PythonPanel ):

        def __init__(self, widget, name, id):
          PythonPanel.__init__(self, name, id )
          self.customKnob = nuke.PyCustom_Knob( name, "", "__import__('nukescripts').panels.WidgetKnob(" + widget + ")" )
          self.addKnob( self.customKnob  )

      def addPanel(pane=None):
        return Panel( widget, name, id ).addToPane(pane=pane)

      menu = nuke.menu('Pane')
      menu.addCommand( name, addPanel)
      registerPanel( id, addPanel )

      if ( create ):
        return Panel( widget, name, id )
      else:
        return None

    if nukescripts.panels.__panels.get('Python.Editor') is not None:
        del nukescripts.panels.__panels['Python.Editor']

    registerWidgetAsPanel('__import__("PythonEditor").ide.IDE',
                          "Python Editor",
                          'Python.Editor')
