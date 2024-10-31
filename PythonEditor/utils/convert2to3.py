# convert code from python 2 to 3
from __future__ import print_function
import traceback

import lib2to3
from lib2to3.main import diff_texts
from lib2to3.refactor import RefactoringTool, get_fixers_from_package


def convert_to_python3(script, verbose=False):
    """Convert a string containing python 2
    syntax to python 3 syntax. The string passed
    must be valid python code without any python 2
    syntax errors.
    
    :param script: `str` python 2 code
    :param verbose: `bool` optionally, print a diff of the changes
    :rtype: `str` python 3 code
    """
    fixers = get_fixers_from_package("lib2to3.fixes")
    refactoring_tool = RefactoringTool(fixer_names=fixers)
    result = refactoring_tool.refactor_string(script, "script")
    new_script = str(result)
    if verbose:
        for line in diff_texts(script, new_script, ""):
            print(line)
    return new_script