def exec_app(app):
    exec_method = getattr(app, "exec", None)
    if exec_method is None:
        exec_method = app.exec_
    return exec_method()
