import sys


class VirtualModule(object):
    def hello(self):
        return 'Hello World!'


class Loader(object):
    """docstring for Loader"""
    def load_module(self, name):
        print name
        return VirtualModule()


class Finder(object):
    """docstring for Finder"""
    def find_module(self, name, path=''):
        print name, path
        if name == 'select':
            return Loader()

# sys.modules['select'] = 'tada'
sys.meta_path.append(Finder())
import os
__folder__ = __file__
for x in range(2):
    __folder__ = os.path.dirname(__folder__)
print __folder__
sys.path.append(__folder__)

import cProfile
import select

print select
# import PythonEditor
# print PythonEditor

