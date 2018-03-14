import inspect
import sys
from pprint import pprint
from types import FunctionType

from PySide import QtGui, QtCore

def code_to_function(code):
    def fn_dummy():
        return None

    fn_dummy.__code__ = code
    return fn_dummy

class menu():
    def __init__(self, name):
        menuDict = {w.objectName():w 
        for w in QtGui.qApp.topLevelWidgets()
        if isinstance(w, QtGui.QMenu)}
        self._menu = menuDict[name]

    def addCommand(self, name, _func, shortcut=None, icon=None):

        if type(_func) == str:
            code = compile(_func, '<NukeApp>', 'exec')
            _func = FunctionType(code, {}, 'fn', ()) 
                # globals[, name[, argdefs[, closure]]])
            # _func = code_to_function(code)

        self._menu.addAction(name, _func)

class PyCustom_Knob(QtGui.QWidget):
    """
    Up until now, this was mimicking the nuke API.
    This __init__ is a total hack.
    """
    def __init__(self, name, label, widgetString):
        super(PyCustom_Knob, self).__init__()
        # print __import__("PythonEditor.IDE").IDE()
        from PythonEditor.IDE import IDE
        self.ide = IDE()
        # self.ide.show()

        mainWindows = [w 
        for w in QtGui.qApp.topLevelWidgets()
        if isinstance(w, QtGui.QMainWindow)]
        mw = mainWindows[0]

        dock1 = QtGui.QDockWidget()
        dock1.setObjectName('PyEditorDock')
        mw.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock1)
        dock1.setWidget(self.ide)

        # raise NotImplementedError, (name, label, widgetString)

def tcl(_str):
    print _str
    global _globals
    global _locals
    _globals = dict(inspect.getmembers(inspect.stack()[1][0]))['f_globals']
    _locals = dict(inspect.getmembers(inspect.stack()[1][0]))['f_globals']
    # pprint(_globals)
    _globals.update({'_globals':_globals})
    _locals.update({'_locals':_locals})
    
def toNode(_str):
    return Node()

def selectedNode():
    return Node()

PyScript_Knob = None
PythonKnob = None

def message(_str):
    print _str

def tprint(_str):
    print _str

class Node(object):
    def begin(self):
        pass
    def __enter__(self):
        pass
    def __exit__(self):
        pass
    def allKnobs():
        pass
    def end(self):
        pass