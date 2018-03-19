import __main__
import traceback

def mainexec(_code):
    """
    Code execution in top level namespace.
    Reformats exceptions to remove 
    references to this file.
    """
    if isinstance(_code, unicode):
        _code = str(_code)

    if isinstance(_code, str):
        if len(_code.strip().split('\n')) == 1:
            mode = 'single'
        else:
            mode = 'exec'

        _code = compile(_code, '<i.d.e>', mode)

    print('# Result: ')
    _ = {}
    try:
        # Ian Thompson is a golden god
        exec(_code, __main__.__dict__, _)
    except Exception:
        formatted_lines = traceback.format_exc().splitlines()[3:]
        print '\n'.join(formatted_lines)

    __main__.__dict__.update(_)
    
    if _ and mode == 'single': print(_)
