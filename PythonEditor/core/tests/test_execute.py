import __main__
import PythonEditor.core.execute as exe


TEST_CODE = """

class A():
    atr = 'test'

a = A()

#&&

import sys

print sys.argv

#&&

import math

def fibo(x):
    return x+1

"""

TEST_FRAGMENT = """
class A():
    atr = 'test'

a = A()
"""

def test_mainexec():
    """Test that variables are executed in the
    top-level interpreter namespace.
    """
    errlineno = exe.mainexec(
        TEST_FRAGMENT,
        TEST_CODE,
        verbosity=exe.VERBOSITY_LOW
    )
    assert __main__.__dict__['a'].atr == 'test'


def test_error_lines():
    """Assert that the correct error line
    number is returned from the mainexec function
    when passed the whole document text.
    """
    whole = str('\n#'*10)+'\n1/0'
    # when the whole document is passed, the
    # text is stripped.
    num_lines = len(whole.strip().splitlines())
    errlineno = exe.mainexec(whole, whole)
    assert errlineno == [num_lines]


def test_error_lines_offset():
    """Assert that the correct error line
    number is returned from the mainexec function
    when passed offset text.
    """
    part = str('\n#'*4)+'\n1/0'
    whole = str('\n#'*10)+'\n1/0'
    num_lines = len(part.splitlines())
    errlineno = exe.mainexec(part, whole)
    assert errlineno == [num_lines]


def test_error_lines_current_line():
    """Assert that the correct error line
    number is returned from the mainexec function
    when passed a single line of text.
    """
    global TEST_CODE
    # first we define fibo in the main namespace
    exe.mainexec(TEST_CODE, TEST_CODE)

    part = 'fibo("four")'

    TEST_CODE += '\n'+part
    num_lines = len(TEST_CODE.splitlines())

    # offset part for traceback
    part = str('\n'*num_lines)+part

    TEST_CODE = '\n'+TEST_CODE

    # then run the actual test that
    # raises an Exception
    errlineno = exe.mainexec(part, TEST_CODE)
    assert errlineno == [22, 19]
