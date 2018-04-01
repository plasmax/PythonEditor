from __main__ import __dict__
import traceback
import sys

def mainexec(text, wholeText):
    """
    Code execution in top level namespace.
    Reformats exceptions to remove 
    references to this file.
    """
    if len(text.strip().split('\n')) == 1:
        mode = 'single'
    else:
        mode = 'exec'

    try:
        _code = compile(text, '<i.d.e>', mode)
    except SyntaxError:
        print_syntax_traceback()
        return

    _ = __dict__.copy()
    print('# Result: ')
    try:
        # Ian Thompson is a golden god
        exec(_code, __dict__)
    except Exception:
        print_traceback(wholeText)
    else:
        if mode == 'single': 
            for value in __dict__.values():
                if  value not in _.values():
                    print(value)
            del _

def print_syntax_traceback():
    """
    Print traceback without lines of 
    the error that refer to this file.
    """
    print('# Python Editor SyntaxError')
    formatted_lines = traceback.format_exc().splitlines()
    print( formatted_lines[0] )
    print( '\n'.join(formatted_lines[3:]) )

def print_traceback(wholeText):
    """
    Print traceback ignoring lines that refer to the
    external execution python file, using the whole 
    text of the document.
    """

    print('# Python Editor Traceback (most recent call last):')
    textlines = wholeText.splitlines()
    msg = '  File "{0}", line {1}, in {2}\n    {3}'
    _, _, exc_tb = sys.exc_info()
    for file, lineno, scope, code in traceback.extract_tb(exc_tb):
        if code is None:
            code = textlines[lineno-1].strip()
        tracemsg = msg.format(file, lineno, scope, code)
        if file != __file__:
            print(tracemsg)
        else:
            pass # TODO: collect and log unusual tracebacks referring to this file

    formatted_lines = traceback.format_exc().splitlines()
    print formatted_lines[-1]