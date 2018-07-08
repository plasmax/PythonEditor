import __main__
import traceback
import re


FILENAME = '<Python Editor Contents>'


def mainexec(text, whole_text):
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
        # try to print new values initialised
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
            if mode == 'single':
                for value in __main__.__dict__.values():
                    try:
                        # sometimes, this causes
                        # SystemError: Objects/longobject.c:244:
                        # bad argument to internal function
                        if value not in namespace.values():
                            print(value)
                    except TypeError:
                        pass
        except (NotImplementedError, AttributeError):
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
    for line in formatted_lines:
        result = re.search('(?<="{0}", line )(\d+)'.format(FILENAME), line)
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
    text_lines = whole_text.splitlines()

    error_message = traceback.format_exc()

    message_lines = []
    error_lines = error_message.splitlines()
    error = error_lines.pop()
    error_line_numbers = []
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
            error_line_numbers.append(lineno)

    message_lines.append(error)
    error_message = '\n'.join(message_lines)
    print(error_message)
    return error_line_numbers
