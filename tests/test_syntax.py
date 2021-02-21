#!/usr/bin/env python3
# git pre-commit hook SyntaxError checker

import os
import sys
import json


PACKAGE_NAME = 'PythonEditor' # this is the only bit that should change from project to project


def get_project_dir():
    folder = os.path.dirname(os.path.abspath(__file__))
    folder_name = os.path.basename(folder)

    # package should be one level up from /tests/
    if folder_name != 'tests':
        raise Exception('This test is designed to be run from a "/tests/" subdirectory, not %s'%folder)

    package_dir = os.path.dirname(folder)

    project_dir = os.path.join(package_dir, PACKAGE_NAME)
    return project_dir


def read(path):
    with open(path, 'r') as fd:
        return fd.read()


def check_py(path):
    contents = read(path)
    compile(contents, path, 'exec')


def check_json(path):
    contents = read(path)
    json.loads(contents)


def main():
    project_dir = get_project_dir()
    for root, dirs, files in os.walk(project_dir):
        for filename in files:
            if filename.endswith('.py'):
                check_py(os.path.join(root, filename))
            if filename.endswith('.json'):
                check_json(os.path.join(root, filename))

    print('Syntax check complete, all .py and .json files compile with Python {}'.format(sys.version))


if __name__ == '__main__':
    main()
