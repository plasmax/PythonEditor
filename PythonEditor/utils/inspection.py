import sys
import inspect
from functools import partial

from ctypes import c_int64 as mutable_int

def test_sys_count(func):
    global count
    count = 0
    def msr(*args, **kwargs):
        global count
        count += 1
        
    sys.setprofile(msr)
    func()
    sys.setprofile(None)
    print('Number of frame objects counted for {0}: {1}'.format(func,count))

def increment(number):
    number.value += 1

def get_called_code(func, *args, **kwargs):
    """
    Returns a string containing source code.
    Sets a temporary profiling function that 
    collects source code from all callables.
    """
    def trace_source(frame, event, arguments, source=[]):
        try:
            if event == 'call':
                try:
                    src = inspect.getsource(frame)
                    file = frame.f_code.co_filename
                    if not any(src == text for f, text, c in source):
                        source.append((file, src, mutable_int(1)))
                    else:
                        for f, text, c in source:
                            if src == text:
                                increment(c)
                except IOError, e:
                    print e, frame.f_code, event, arguments, '\n'*5
        except Exception, e:
            sys.setprofile(None)
            print 'Trace Source Quitting on Error:', e
        
    srccode = []
    prof = partial(trace_source, source=srccode)                                
    sys.setprofile(prof)
    func.__call__(*args, **kwargs)
    sys.setprofile(None)

    def info(filename, sourcecode, count):
        spacing = '\n'*3
        file_text = 'Filename: '
        count_text = 'Number of times called: '
        string = '{0}# {1}{2}\n# {3}{4}\n{5}' 
        return string.format(spacing,
                            file_text,
                            filename,
                            count_text,
                            count.value,
                            sourcecode,)

    source_code = ''.join([info(*a) for a in srccode])
    if source_code == '':
        print 'No source code could be retrieved.'
    return source_code
    
