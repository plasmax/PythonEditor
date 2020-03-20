import __main__
import traceback
import re


FILENAME = '<Python Editor Contents>'
VERBOSITY_LOW = 0
VERBOSITY_HIGH = 1

def mainexec(text, whole_text, verbosity=VERBOSITY_LOW):
    """
    Code execution in top level namespace.
    Reformats exceptions to remove
    references to this file.

    :param text: code to execute
    :param whole_text: all text in document
    :type text: str
    :type whole_text: str
    """
    if len(text.strip().split('\n')) == 1:
        mode = 'single'
    else:
        mode = 'exec'
    try:
        _code = compile(text, FILENAME, mode)
    except SyntaxError:
        error_line_numbers = print_syntax_traceback()
        return error_line_numbers

    namespace = __main__.__dict__.copy()
    print('# Result: ')
    try:
        # Ian Thompson is a golden god
        exec(_code, __main__.__dict__)
    except Exception as e:
        error_line_numbers = print_traceback(whole_text, e)
        return error_line_numbers
    else:
        if verbosity == VERBOSITY_LOW:
            return
        # try to print new assigned values
        if mode != 'single':
            return

        not_dicts = not all([
            isinstance(namespace, dict),
            isinstance(__main__.__dict__, dict),
            hasattr(namespace, 'values')
        ])

        if not_dicts:
            return None

        try:
            for key, value in __main__.__dict__.items():
                if value not in namespace.values():
                    try:
                        print(value)
                    except Exception:
                        # if the value throws an error here,
                        # try to remove it from globals.
                        del __main__.__dict__[key]
        except Exception:
            # if there's an error in iterating through the
            # interpreter globals, restore the globals one
            # by one until the offending value is removed.
            __copy = __main__.__dict__.copy()
            __main__.__dict__.clear()
            for key, value in __copy.items():
                try:
                    __main__.__dict__.update({key:value})
                except Exception:
                    print("Couldn't restore ", key, value, "into main globals")

            # TODO: do some logging here.
            # sometimes, this causes
            # SystemError: Objects/longobject.c:244:
            # TypeError('vars() argument must have __dict__ attribute',)
            # bad argument to internal function
            # NotImplementedError, AttributeError, TypeError, SystemError
            return None


def print_syntax_traceback():
    """
    Print traceback without lines of
    the error that refer to this file.
    """
    print('# Python Editor SyntaxError')
    formatted_lines = traceback.format_exc().splitlines()
    print(formatted_lines[0])
    print('\n'.join(formatted_lines[3:]))

    error_line_numbers = []
    global FILENAME
    pattern = r'(?<="{0}",\sline\s)(\d+)'.format(FILENAME)
    for line in formatted_lines:
        result = re.search(pattern, line)
        if result:
            lineno = int(result.group())
            error_line_numbers.append(lineno)
    return error_line_numbers


def print_traceback(whole_text, error):
    """
    Print traceback ignoring lines that refer to the
    external execution python file, using the whole
    text of the document. Extracts lines of code from
    whole_text that caused the error.

    :param whole_text: all text in document
    :param error: python exception object
    :type whole_text: str
    :type error: exceptions.Exception
    """
    text_lines = whole_text.split('\n')
    num_lines = len(text_lines)

    error_message = traceback.format_exc()

    global FILENAME
    pattern = r'(?<="{0}",\sline\s)(\d+)'.format(FILENAME)

    message_lines = []
    error_lines = error_message.splitlines()
    error = error_lines.pop()
    error_line_numbers = []
    exec_string = 'exec(_code, __main__.__dict__)'
    for line in error_lines:
        if (__file__ in line
                or exec_string in line):
            continue

        message_lines.append(line)

        result = re.search(pattern, line)
        if result:
            lineno = int(result.group())
            while lineno >= num_lines:
                # FIXME: this exists to patch a logical fault
                # When text is selected and there is no newline
                # afterwards, the lineno can exceed the number
                # of lines in the text_lines list. ideally, no
                # whole_text would be provided that can exceed
                # this limit
                lineno -= 1
            text = '    ' + text_lines[lineno].strip()
            message_lines.append(text)
            error_line_numbers.append(lineno)
    message_lines.append(error)
    error_message = '\n'.join(message_lines)
    print(error_message)
    return error_line_numbers
