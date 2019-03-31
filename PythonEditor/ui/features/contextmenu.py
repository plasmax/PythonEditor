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
from PythonEditor.ui.features import actions


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
        self.menu_setup()
        menu.exec_(QtGui.QCursor().pos())

    def menu_setup(self):
        self.menu.addSeparator()

        for widget, action_name, attributes in actions.class_actions(self):
            location = attributes.get('Menu Location')
            if location is None:
                continue
            for action in widget.actions():
                if action.text() != action_name:
                    continue
                break
            else:
                continue

            menu = self.menu
            if location != '':
                for name in location.split('/'):
                    item = actions.find_menu_item(menu, name)
                    if item is None:
                        item = menu.addMenu(name)
                    menu = item
            menu.addAction(action)

        return

        # TODO: migrate to actions
        self.info_menu = self.menu.addMenu('Info')
        for var in ('globals', 'locals', 'environ'):
            print_var = partial(
                self.print_info,
                var
            )
            self.info_menu.addAction(
                'Print {0}'.format(var),
                print_var
            )

        self.snippet_menu = self.menu.addMenu('Snippets')
        self.utils_menu = self.snippet_menu.addMenu('Utils')

        for snippet in self.snippetDict.keys():
            snippet_insert = partial(self.insert_snippet, snippet)
            self.snippet_menu.addAction(
                snippet,
                snippet_insert
            )

        self.add_nuke_specific_menu_items()

        cursor = self.editor.textCursor()
        self.selectedText = str(cursor.selectedText().encode('utf-8').strip())

        if self.selectedText != '':
            for info in ['help', 'type', 'dir', 'len', 'getattr', 'pprint']:
                text = self.selectedText
                print_info = partial(self.print_info,
                                     info, text=text)
                self.info_menu.addAction('Print {0}'.format(info),
                                        print_info)

            # conditional on text selected and external editor path verified
            self.editor_menu = self.menu.addMenu('External Editor')
            self.editor_menu.addAction('Open Module File',
                                      self._open_module_file)
            self.editor_menu.addAction('Open Module Directory',
                                      self._open_module_directory)
            self.editor_menu.addAction('Copy to External Editor',
                                      self.notImplemented)

            # conditional on text selected and inspect.isModule
            self.inspect_menu = self.menu.addMenu('Inspect')
            self.inspectIsMenu = self.inspect_menu.addMenu('is')
            self.inspectGetMenu = self.inspect_menu.addMenu('get')
            # self.inspect_menu.addAction('Inspect', print(self.inspectDict))
            for attr in self.inspectDict.keys():
                func = partial(self.inspectExec, attr)
                if attr.startswith('is'):
                    self.inspectIsMenu.addAction(attr, func)
                elif attr.startswith('get'):
                    self.inspectGetMenu.addAction(attr, func)
                else:
                    self.inspect_menu.addAction(attr, func)

            # http://doc.qt.io/archives/qt-4.8/qrubberband.html
            # http://doc.qt.io/archives/qt-4.8/classes.html
            self.menu.addAction('Open Qt Docs', self.notImplemented)

    def add_nuke_specific_menu_items(self):
        try:
            import nuke
        except ImportError:
            return

        self.nodes_menu = self.menu.addMenu('Nodes')
        self.nodes_add_menu = self.nodes_menu.addMenu('Add knob')
        self.nodes_set_menu = self.nodes_menu.addMenu('Set')
        self.nodes_get_menu = self.nodes_menu.addMenu('Get')
        self.nodes_clr_menu = self.nodes_menu.addMenu('Clear')
        self.nodes_run_menu = self.nodes_menu.addMenu('Eval in Knob Context')

        # TODO: these could be conditional on nodes selected
        pyknobs = set([
            'knobChanged',
            'onCreate',
            'beforeRender',
            'beforeFrameRender',
        ])

        knob_types = (nuke.PyCustom_Knob,
                      nuke.PythonKnob,
                      nuke.PythonCustomKnob,
                      nuke.PyScript_Knob)

        # get common python knobs
        for node in nuke.selectedNodes():
            for knob in node.allKnobs():
                if isinstance(knob, knob_types):
                    pyknobs.add(knob.name())

        for node in nuke.selectedNodes():
            for knob_name in pyknobs.copy():
                if node.knob(knob_name) is None:
                    pyknobs.remove(knob_name)

        for knob_name in pyknobs:
            func = partial(self.set_knob_value, knob_name)
            self.nodes_set_menu.addAction(knob_name, func)

        for knob_name in pyknobs:
            func = partial(self.get_knob_value, knob_name)
            self.nodes_get_menu.addAction(knob_name, func)

        for knob_name in pyknobs:
            func = partial(self.clr_knob_value, knob_name)
            self.nodes_clr_menu.addAction(knob_name, func)

        for knob_name in pyknobs:
            func = partial(self.run_knob_value, knob_name)
            self.nodes_run_menu.addAction(knob_name, func)

        problem_knobs = ('Obsolete_Knob', 'GeoSelect_Knob')
        add_knobs = {name: knob for name, knob in nuke.__dict__.items()
                 if '_Knob' in name
                 and name not in problem_knobs}
        #knobs['Boolean_Knob'].__new__(knobs['Boolean_Knob'], 'name', 'label')

        for knob_name in add_knobs:
            func = partial(self.add_knob, knob_name)
            self.nodes_add_menu.addAction(knob_name, func)

    def notImplemented(self):
        raise NotImplementedError('not implemented yet')

    def add_knob(self, knob_name='knobChanged'):
        # TODO: this is only a test feature, the best way to quickly add knobs
        # would be through autocompletion on the addKnob method
        import nuke
        problem_knobs = ('Obsolete_Knob', 'GeoSelect_Knob')
        add_knobs = {name: knob for name, knob in nuke.__dict__.items()
                 if '_Knob' in name
                 and name not in problem_knobs}
        for node in nuke.selectedNodes():
            knob = add_knobs[knob_name].__new__(add_knobs[knob_name], 'name', 'label')
            node.addKnob(knob)

    def set_knob_value(self, knob_name='knobChanged'):
        import nuke
        self.textCursor = self.editor.textCursor()
        text = self.textCursor.selection().toPlainText()
        # text = self.textCursor.selectedText().encode('utf-8').splitlines()
        # if not ''.join(text).strip():
        if not text.strip():
            text = self.editor.toPlainText()

        for node in nuke.selectedNodes():
            node.knob(knob_name).setValue(text)
            print(node.fullName(), 'set:', knob_name, '\n', text)

    def get_knob_value(self, knob_name='knobChanged'):
        import nuke

        for node in nuke.selectedNodes():
            knob = node.knob(knob_name)
            if knob is not None:
                description = '# %s.%s\n' % (node.fullName(), knob.name())
                self.editor.insertPlainText(description)
                self.editor.insertPlainText(knob.value())

    def clr_knob_value(self, knob_name='knobChanged'):
        import nuke

        for node in nuke.selectedNodes():
            knob = node.knob(knob_name)
            if knob is not None:
                knob.setValue('')

    def run_knob_value(self, knob_name='knobChanged'):
        import nuke

        self.textCursor = self.editor.textCursor()
        text = self.textCursor.selectedText().encode('utf-8')
        if not text.strip():
            text = self.editor.toPlainText()

        for node in nuke.selectedNodes():
            knob = node.knob(knob_name)
            if knob is not None:
                nuke.runIn(knob.fullyQualifiedName(), text)

    # FIXME: Moved to actions. Delete
    def printHelp(self):
        text = self.selectedText
        obj = actions.get_subobject(text)
        if obj is not None:
            print(obj.__doc__)

    # FIXME: Moved to actions. Delete
    def _open_module_file(self):
        text = str(self.selectedText)
        obj = actions.get_subobject(text)
        actions.open_module_file(obj)

    # FIXME: Moved to actions. Delete
    def _open_module_directory(self):
        text = str(self.selectedText)
        obj = actions.get_subobject(text)
        actions.open_module_directory(obj)

    def initInspectDict(self):
        """
        Creates a dictionary of functions
        from the inspect module.
        """
        self.inspectDict = {
            func: getattr(inspect, func)
            for func in dir(inspect)
            if isinstance(getattr(inspect, func),
                          types.FunctionType)
        }

    def inspectExec(self, func):
        """
        Call a function from the inspect
        module using the selected text as the
        input parameter and print the result.
        """
        cursor = self.editor.textCursor()
        selection = cursor.selection()
        text = selection.toPlainText()
        if not text.strip():
            return
        obj = actions.get_subobject(text)
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

    def print_info(self, keyword, text=''):
        if keyword == 'globals':
            pprint(__main__.__dict__)
        elif keyword == 'locals':
            print(__main__.__dict__)
        elif keyword == 'environ':
            pprint(os.environ.copy())

        obj = __main__.__dict__.get(text)
        if obj is None:
            return

        if keyword == 'dir':
            pprint(dir(obj))
        elif keyword == 'help':
            print(help(obj))
        elif keyword == 'type':
            print(type(obj))
        elif keyword == 'len':
            print(len(obj))
        elif keyword == 'getattr':
            attrs = {attr: getattr(obj, attr) for attr in dir(obj)}
            pprint(attrs)
        elif keyword == 'pprint':
            print(obj)
