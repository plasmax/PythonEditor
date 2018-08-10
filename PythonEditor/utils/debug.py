from __future__ import print_function
import os
import sys
import inspect


def debug(*args, **kwargs):
    if os.getenv('USER') != 'mlast':
        return

    f = sys._getframe().f_back
    
    print('\nDEBUG:')

    print(*args, **kwargs)

    _file = inspect.getfile(f)
    lineno = str(inspect.getlineno(f))
    print('sublime %s:%s' % (_file, lineno))
