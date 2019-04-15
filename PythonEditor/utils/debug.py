from __future__ import print_function
import os
import sys
import inspect


def print_call_stack():
    stack = []
    f = sys._getframe()
    while f is not None:
        stack.append(f)
        f = f.f_back
    s = ''
    for f in reversed(stack):
        _name = f.f_globals.get('__name__')
        l = '{0}{1} in {2}'.format(
            s,
            f.f_code.co_name,
            _name
        )
        print(l)
        s+=' '


def debug(*args, **kwargs):
    """
    For exclusively printing to mlast user terminal.
    TODO: what more useful information could be included here?
    Would be nice to allow this to send information via email.
    """
    try:
        if os.getenv('USER') != 'mlast':
            return

        f = sys._getframe().f_back

        print('\nDEBUG:')
        print(*args, **kwargs)
        if 'print_call_stack' in kwargs:
            print_call_stack()

        _file = inspect.getfile(f)
        lineno = str(inspect.getlineno(f))
        print('sublime %s:%s' % (_file, lineno))
    except:
        pass
