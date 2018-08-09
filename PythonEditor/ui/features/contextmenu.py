from __future__ import print_function
import os
import sys
import inspect
import types
import __main__
import subprocess
from functools import partial
from pprint import pprint
from PythonEditor.ui.Qt import QtWidgets, QtGui, QtCore
from PythonEditor.utils import constants


def get_subobject(text):
    if '.' in text:
        name = text.split('.')[0]
        obj = __main__.__dict__.get(name)
        for name in text.split('.')[1:]:
            obj = getattr(obj, name)
    else:
        obj = __main__.__dict__.get(text)

    return obj


def open_module_file(obj):
    try:
        file = inspect.getfile(obj)
    except TypeError as e:
        if hasattr(obj, '__class__'):
            obj = obj.__class__
            file = inspect.getfile(obj)
        else:
            raise TypeError(e)

    if file.endswith('.pyc'):
        file = file.replace('.pyc', '.py')

    try:
        lines, lineno = inspect.getsourcelines(obj)
        file = file+':'+str(lineno)
    except AttributeError:
        pass

    print(file)
    EXTERNAL_EDITOR_PATH = constants.get_external_editor_path()
    if (EXTERNAL_EDITOR_PATH
            and os.path.isdir(os.path.dirname(EXTERNAL_EDITOR_PATH))):
        subprocess.Popen([EXTERNAL_EDITOR_PATH, file])


def open_module_directory(obj):
    file = inspect.getfile(obj).replace('.pyc', '.py')
    folder = os.path.dirname(file)
    print(folder)
    EXTERNAL_EDITOR_PATH = constants.get_external_editor_path()
    if (EXTERNAL_EDITOR_PATH
            and os.path.isdir(os.path.dirname(EXTERNAL_EDITOR_PATH))):
        subprocess.Popen([EXTERNAL_EDITOR_PATH, folder])


def openDir(module):
    try:
        print(bytes(module.__file__))
        subprocess.Popen(['nautilus', module.__file__])
    except AttributeError:
        file = inspect.getfile(module)
        subprocess.Popen(['nautilus', file])
    print('sublime ', __file__, ':', sys._getframe().f_lineno, sep='')  # TODO: nautilus is not multiplatform!


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
        raise NotImplementedError('not implemented yet')

    def setKnobScript(self, knobName='knobChanged'):
        self.textCursor = self.editor.textCursor()
        text = self.textCursor.selectedText().encode('utf-8')

        for node in nuke.selectedNodes():
            node.knob(knobName).setValue(text)
            print(node.fullName(), 'set:', knobName)

    def searchInput(self):
        """
        Very basic search dialog.
        TODO: Create a QAction and store
        this in utils so that it can be
        linked to Ctrl + F as well.
        """

        dialog = QtWidgets.QInputDialog.getText(
            self.editor, 'Search', '')
        text, ok = dialog
        if not ok:
            return

        textCursor = self.editor.textCursor()
        document = self.editor.document()
        cursor = document.find(text, textCursor)
        self.editor.setTextCursor(cursor)

    def printHelp(self):
        text = self.selectedText
        obj = get_subobject(text)
        if obj is not None:
            print(obj.__doc__)

    def _open_module_file(self):
        text = str(self.selectedText)
        obj = get_subobject(text)
        open_module_file(obj)

    def _open_module_directory(self):
        text = str(self.selectedText)
        obj = get_subobject(text)
        open_module_directory(obj)

    def initInspectDict(self):
        self.inspectDict = {func: getattr(inspect, func)
                            for func in dir(inspect)
                            if isinstance(getattr(inspect, func),
                                          types.FunctionType)}

    def inspectExec(self, func):
        """
        TODO: not sure this works...
        """
        text = str(self.selectedText)
        obj = get_subobject(text)
        if obj is None:
            return
        print(self.inspectDict.get(func).__call__(obj))

    def initSnippetDict(self):
        """
        Creates a basic snippet dictionary.
        TODO: Add some nice getter/setters
        and JSON file parsing to store and
        read larger snippet samples.
        """
        pkn = 'print nuke.thisKnob().name()'
        nsn = 'nuke.selectedNode()'
        fns = 'for node in nuke.selectedNodes():'
        fna = 'for node in nuke.allNodes():'
        ppa = 'pprint({attr:getattr(obj, attr) for attr in dir(obj)})'
        nid = '_nuke_internal.debugBreakPoint()'
        self.snippetDict = {
            pkn: pkn,
            nsn: nsn,
            fns: fns + '\n    ',
            fna: fna + '\n    ',
            ppa: ppa,
            nid: nid,
        }

    def new_snippet(self):
        """
        Save a new snippet to JSON file.
        """
        raise NotImplementedError('save new snippet')

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
            print(__main__.__dict__)

        obj = __main__.__dict__.get(text)
        if obj is None:
            return

        if keyword == 'dir':
            pprint(dir(obj))
        elif keyword == 'environ':
            pprint(os.environ.copy())
        elif keyword == 'help':
            print(help(obj))
        elif keyword == 'type':
            print(type(obj))
        elif keyword == 'len':
            print(len(obj))
        elif keyword == 'getattr':
            attrs = {attr: getattr(obj, attr) for attr in dir(obj)}
            pprint(attrs)

    def menuSetup(self):
        self.menu.addAction('Save As', self.notImplemented)
        self.menu.addAction('Search', self.searchInput)

        self.infoMenu = self.menu.addMenu('Info')

        print_globals = partial(self.printInfo, 'globals')
        self.infoMenu.addAction('Print globals',
                                print_globals)
        print_locals = partial(self.printInfo, 'locals')
        self.infoMenu.addAction('Print locals',
                                print_locals)
        print_environ = partial(self.printInfo, 'environ')
        self.infoMenu.addAction('Print environ',
                                print_environ)

        self.snippetMenu = self.menu.addMenu('Snippets')
        self.utilsMenu = self.snippetMenu.addMenu('Utils')

        for snippet in self.snippetDict.keys():
            snippet_insert = partial(self.insert_snippet, snippet)
            self.snippetMenu.addAction(snippet,
                                       snippet_insert)

        cursor = self.editor.textCursor()
        self.selectedText = str(cursor.selectedText().encode('utf-8').strip())

        if self.selectedText != '':
            for info in ['help', 'type', 'dir', 'len', 'getattr']:
                text = self.selectedText
                print_info = partial(self.printInfo,
                                     info, text=text)
                self.infoMenu.addAction('Print {0}'.format(info),
                                        print_info)

            # TODO: these could be conditional on nodes selected
            self.nodesMenu = self.menu.addMenu('Nodes')
            self.nodesMenu.addAction('Run on All Nodes',
                                     self.notImplemented)
            self.nodesMenu.addAction('Run on Selected Nodes',
                                     self.notImplemented)
            pyknobs = ['knobChanged',
                       'onCreate',
                       'beforeRender',
                       'beforeFrameRender']
            for knob in pyknobs:
                title = 'Copy to Nodes {0}'.format(knob)
                func = partial(self.setKnobScript, knob)
                self.nodesMenu.addAction(title, func)

            # conditional on text selected and external editor path verified
            self.editorMenu = self.menu.addMenu('External Editor')
            self.editorMenu.addAction('Open Module File',
                                      self._open_module_file)
            self.editorMenu.addAction('Open Module Directory',
                                      self._open_module_directory)
            self.editorMenu.addAction('Copy to External Editor',
                                      self.notImplemented)

            # conditional on text selected and inspect.isModule
            self.inspectMenu = self.menu.addMenu('Inspect')
            self.inspectIsMenu = self.inspectMenu.addMenu('is')
            self.inspectGetMenu = self.inspectMenu.addMenu('get')
            # self.inspectMenu.addAction('Inspect', print(self.inspectDict))
            for attr in self.inspectDict.keys():
                func = partial(self.inspectExec, attr)
                if attr.startswith('is'):
                    self.inspectIsMenu.addAction(attr, func)
                elif attr.startswith('get'):
                    self.inspectGetMenu.addAction(attr, func)
                else:
                    self.inspectMenu.addAction(attr, func)

            # http://doc.qt.io/archives/qt-4.8/qrubberband.html
            # http://doc.qt.io/archives/qt-4.8/classes.html
            self.menu.addAction('Open Qt Docs', self.notImplemented)
