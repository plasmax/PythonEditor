import PythonEditor


def test_panel_registered():
    try:
        import nukescripts
    except ImportError:
        print('This test can only be run in Nuke')
        return
    assert nukescripts.panels.__panels.get('Python.Editor') is not None
