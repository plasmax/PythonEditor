def setup_dock():
    try:
        from nukescripts import registerWidgetAsPanel
    except ImportError:
        return

    registerWidgetAsPanel('__import__("PythonEditor").ide.IDE',
                          "Python Editor",
                          'i.d.e.Python_Editor')
