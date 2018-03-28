import os
import inspect
import types
import __main__
import subprocess
from functools import partial
from pprint import pprint
from PythonEditor.ui.Qt import QtWidgets, QtGui, QtCore

def open_module_file(obj):
    file = inspect.getfile(obj).replace('.pyc', '.py')
    print file
    SUBLIME_PATH = os.environ.get('SUBLIME_PATH')
    if (SUBLIME_PATH
            and os.path.isdir(os.path.dirname(SUBLIME_PATH))):
        subprocess.Popen([SUBLIME_PATH, file]) 
        
def openDir(module):
    try:
        print bytes(module.__file__)
        subprocess.Popen(['nautilus', module.__file__]) 
    except AttributeError:
        file = inspect.getfile(module)
        subprocess.Popen(['nautilus', file])

class ContextMenu(QtCore.QObject):
    def __init__(self, editor):
        super(ContextMenu, self).__init__()
        self.editor = editor
        editor.context_menu_signal.connect(self.show_menu)
        self.initSnippetDict()
        self.initInspectDict()

    @QtCore.Slot(QtWidgets.QMenu)
    def show_menu(self, menu):
        self.menu = menu
        self.menuSetup()
        menu.exec_(QtGui.QCursor().pos())

    def notImplemented(self):
        raise NotImplementedError, 'not implemented yet'

    def setKnobScript(self, knobName='knobChanged'):
        self.textCursor = self.editor.textCursor()
        text = self.textCursor.selectedText().encode('utf-8')#.strip()
        # text = self.selectedText
        for node in nuke.selectedNodes():
            node.knob(knobName).setValue(text)
            print node.fullName(), 'set:', knobName

    def searchInput(self):
        """
        Very basic search dialog.
        TODO: Create a QAction and store
        this in utils so that it can be 
        linked to Ctrl + F as well.
        """

        dialog = QtWidgets.QInputDialog.getText(self.editor, 'Search', '')
        text, ok = dialog
        if not ok:
            return

        textCursor = self.editor.textCursor()
        document = self.editor.document()
        cursor = document.find(text, textCursor)
        pos = cursor.position()
        self.editor.setTextCursor(cursor)

    def printHelp(self):
        selectedText = self.selectedText
        obj = __main__.__dict__.get(text)
        if obj is not None:
            print obj.__doc__

    def open_module_file(self):
        text = str(self.selectedText)
        obj = __main__.__dict__.get(text)
        open_module_file(obj)
        
    def initInspectDict(self):

        self.inspectDict = {func:getattr(inspect, func) 
                            for func in dir(inspect)
                            if isinstance(getattr(inspect, func) , types.FunctionType)}

    def inspectExec(self, func):
        text = str(self.selectedText)
        obj = __main__.__dict__.get(text)
        if obj is None:
            return
        print self.inspectDict.get(func).__call__(obj)

    def initSnippetDict(self):
        """
        Creates a basic snippet dictionary.
        TODO: Add some nice getter/setters 
        and JSON file parsing to store and 
        read larger snippet samples.
        """
        self.snippetDict = {
        'print nuke.thisKnob().name()' : 'print nuke.thisKnob().name()',
        'print nuke.thisNode().name()' : 'print nuke.thisNode().name()',
        'nuke.selectedNode()' : 'nuke.selectedNode()',
        'for node in nuke.selectedNodes():' : 'for node in nuke.selectedNodes():',
        'for node in nuke.allNodes():' : 'for node in nuke.allNodes():',
        'pprint({attr:getattr(obj, attr) for attr in dir(obj)})' : 'pprint({attr:getattr(obj, attr) for attr in dir(obj)})',
        '_nuke_internal.debugBreakPoint()' : '_nuke_internal.debugBreakPoint()',
        }

    def new_snippet(self):
        """
        Save a new snippet to JSON file.
        """
        raise NotImplementedError, 'save new snippet'

    def insert_snippet(self, snippet):
        self.textCursor = self.editor.textCursor()
        self.textCursor.insertText(self.snippetDict.get(snippet))

    def openUtil(self, path):
        with open(path, 'r') as f:
            text = f.read()
        self.textCursor = self.editor.textCursor()
        self.textCursor.insertText(text)

    def printInfo(self, keyword, text=''):
        if keyword == 'globals':
            pprint(__main__.__dict__)
        elif keyword == 'locals':
            print __main__.__dict__

        obj = __main__.__dict__.get(text)
        if obj is None:
            return

        if keyword == 'dir':
            pprint(dir(obj))
        elif keyword == 'environ':
            pprint(os.environ.copy())
        elif keyword == 'help':
            print help(obj)
        elif keyword == 'type':
            print type(obj)
        elif keyword == 'len':
            print len(obj)
        elif keyword == 'getattr':
            attrs = {attr:getattr(obj, attr) for attr in dir(obj)}
            pprint(attrs)

    def menuSetup(self):
        self.menu.addAction('Save As', self.notImplemented)
        self.menu.addAction('Search', self.searchInput)

        self.infoMenu = self.menu.addMenu('Info')
        self.infoMenu.addAction('Print globals', 
            lambda keyword='globals': self.printInfo(keyword))
        self.infoMenu.addAction('Print locals', 
            lambda keyword='locals': self.printInfo(keyword))
        self.infoMenu.addAction('Print environ', 
            lambda keyword='environ': self.printInfo(keyword))

        self.snippetMenu = self.menu.addMenu('Snippets')
        self.utilsMenu = self.snippetMenu.addMenu('Utils')

        for snippet in self.snippetDict.keys():
            self.snippetMenu.addAction(snippet, partial(self.insert_snippet, snippet))

        # utildir = '/net/homes/mlast/.nuke/python/max/gear/utils/'
        # for util in os.listdir(utildir):
        #     self.utilsMenu.addAction(util,
        #         partial(self.openUtil, os.path.join(utildir, util))) 
        #         # lambda path=os.path.join(util,path): self.openUtil(path))

        # all of these should be conditional on text selected! trigger separate method to process
        #print globals(), locals(), dir(), getattrs,
        cursor = self.editor.textCursor()
        self.selectedText = str(cursor.selectedText().encode('utf-8').strip())

        print self.selectedText
        if self.selectedText != '':
            for info in ['help', 'type', 'dir', 'len', 'getattr']:
                self.infoMenu.addAction('Print {}'.format(info), 
                    lambda keyword=info, 
                    text=self.selectedText: self.printInfo(keyword, 
                        text=self.selectedText))

            #TODO: these could be conditional on nodes selected
            self.nodesMenu = self.menu.addMenu('Nodes')
            self.nodesMenu.addAction('Run on All Nodes', self.notImplemented)
            self.nodesMenu.addAction('Run on Selected Nodes', self.notImplemented)
            for knob in ['knobChanged', 'onCreate', 'beforeRender', 'beforeFrameRender']:
                self.nodesMenu.addAction('Copy to Nodes %s'%knob, 
                    lambda knobName=knob: self.setKnobScript(knobName))

            #conditional on text selected and sublime path verified
            self.sublimeMenu = self.menu.addMenu('Sublime')
            self.sublimeMenu.addAction('Open Module File', self.open_module_file)
            self.sublimeMenu.addAction('Copy to Sublime', self.notImplemented) #/net/homes/mlast/.nuke/python/_scriptEditor

            #conditional on text selected and inspect.isModule
            self.inspectMenu = self.menu.addMenu('Inspect')
            self.inspectIsMenu = self.inspectMenu.addMenu('is')
            self.inspectGetMenu = self.inspectMenu.addMenu('get')
            # self.inspectMenu.addAction('Inspect', print(self.inspectDict))
            for func in self.inspectDict.keys():
                if func.startswith('is'):
                    self.inspectIsMenu.addAction(func, 
                        lambda func=func: self.inspectExec(func))
                elif func.startswith('get'):
                    self.inspectGetMenu.addAction(func, 
                        lambda func=func: self.inspectExec(func))
                else:
                    self.inspectMenu.addAction(func, 
                        lambda func=func: self.inspectExec(func))

            #http://doc.qt.io/archives/qt-4.8/qrubberband.html
            self.menu.addAction('Open Qt Docs', self.notImplemented) # http://doc.qt.io/archives/qt-4.8/classes.html

