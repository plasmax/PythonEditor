from __main__ import __dict__
import traceback
import sys
import re

FILENAME = '<Python Editor Contents>'
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
        _code = compile(text, FILENAME, mode)
    except SyntaxError:
        print_syntax_traceback()
        return

    _ = __dict__.copy()
    print('# Result: ')
    try:
        # Ian Thompson is a golden god
        exec(_code, __dict__)
    except Exception as e:
        print_traceback(wholeText, e)
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

def print_traceback(wholeText, error):
    """
    Print traceback ignoring lines that refer to the
    external execution python file, using the whole 
    text of the document. Extracts lines of code from
    wholeText that caused the error.
    """
    text_lines = wholeText.splitlines()

    error_message = traceback.format_exc()

    message_lines = []
    error_lines = error_message.splitlines()
    error = error_lines.pop()
    for line in error_lines:
        if (__file__ in line 
                or 'exec(_code, __dict__)' in line):
            continue

        message_lines.append(line)

        result = re.search('(?<="{0}", line )(\d+)'.format(FILENAME), line)
        if result:
            lineno = int(result.group())
            text = '    ' + text_lines[lineno].strip()
            message_lines.append(text)

    message_lines.append(error)
    error_message = '\n'.join(message_lines)
    print(error_message)
