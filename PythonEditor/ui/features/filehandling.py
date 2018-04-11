from __future__ import unicode_literals
from __future__ import print_function
import os
import time
import uuid
from xml.etree import ElementTree
from PythonEditor.ui.Qt import QtCore, QtWidgets
from PythonEditor.utils.constants import (AUTOSAVE_FILE, 
                                          XML_HEADER,
                                          create_autosave_file)

class FileHandler(QtCore.QObject):
    """
    Simple xml text storage.
    """
    restore_tab_signal = QtCore.Signal(str)

    def __init__(self, editortabs, tab_index=None):
        super(FileHandler, self).__init__()
        self.setObjectName('TabFileHandler')
        create_autosave_file()

        self.editortabs = editortabs
        self.setParent(editortabs)

        #connect tab signals
        tss = editortabs.tab_switched_signal 
        tss.connect(self.tab_switch_handler)
        tcr = editortabs.tabCloseRequested
        tcr.connect(self.removeempty)

        self.setEditor()
        self.readautosave()

    @QtCore.Slot(int, int, bool)
    def tab_switch_handler(self, previous, current, tabremoved):
        if not tabremoved:  #nothing's been deleted
                            #so we need to disconnect
                            #signals from previous editor
            self.disconnectSignals()

        self.setEditor()

    def setEditor(self):
        """
        Sets the current editor
        and connects signals.
        """
        editor = self.editortabs.currentWidget()
        editorChanged = True if not hasattr(self, 'editor') else self.editor != editor
        isEditor = editor.objectName() == 'Editor'
        if isEditor and editorChanged:
            self.editor = editor
            self.connectSignals()

    def connectSignals(self):
        # try:
        #     QtCore.Qt.UniqueConnection
        # except AttributeError as e:
        #     print(e)
        #     QtCore.Qt.UniqueConnection = 128
        self.editor.textChanged.connect(self.autosave)#, QtCore.Qt.UniqueConnection) 
        #document().modificationChanged ? 

    def disconnectSignals(self):
        if not hasattr(self, 'editor'):
            return
        self.editor.textChanged.disconnect()

    def readfile(self, path):
        """
        Opens any file and sets the editor's contents
        to the file's contents. Changes .pyc to .py in 
        path arguments.
        """
        if '.xml' in path:
            return self.readxml(path)

        path = path.replace('.pyc', '.py') #do not open compiled python files

        with open(path, 'r') as f:
            text = f.read()
        self.editor.setPlainText(text)

    def readxml(self, path):
        parser = ElementTree.parse(path)
        root = parser.getroot()
        self.editor.setPlainText(root.text)

    def writexml(self, root, path=AUTOSAVE_FILE):
        data = ElementTree.tostring(root)
        data = data.decode('utf-8')
        data = data.replace('><subscript','>\n<subscript')
        data = data.replace('</subscript><','</subscript>\n<')
        with open(path, 'wt') as f:
            f.write(XML_HEADER+data)

    def parsexml(self, element_name, path=AUTOSAVE_FILE):
        if not create_autosave_file():
            return
        parser = ElementTree.parse(path)
        root = parser.getroot()
        elements = root.findall(element_name)
        return root, elements 

    def readautosave(self):
        """
        Sets editor text content. First checks the 
        autosave file for <subscript> elements and
        creates a tab per element.
        """
        root, subscripts = self.parsexml('subscript')

        editor_count = 0
        for s in subscripts:
                
            if not s.text:
                root.remove(s)
                continue

            editor_count += 1

            editor = self.editortabs.new_tab()
            tab_index = str(self.editortabs.currentIndex())
            s.attrib['uuid'] = editor.uid
            editor.setPlainText(s.text)

        if editor_count == 0:
            self.editortabs.new_tab()

        self.writexml(root)

    @QtCore.Slot()
    def autosave(self):
        """
        Saves editor contents into autosave
        file with a unique identifier (uuid).
        """
        root, subscripts = self.parsexml('subscript')

        tab_index = str(self.editortabs.currentIndex())

        found = False
        for s in subscripts:
            if s.attrib.get('uuid') == self.editor.uid:
                s.text = self.editor.toPlainText()
                found = True

        if not found:
            sub = ElementTree.Element('subscript')
            sub.attrib['uuid'] = self.editor.uid
            root.append(sub)
            sub.text = self.editor.toPlainText()
   
        self.writexml(root)

    @QtCore.Slot(int)
    def removeempty(self, tab_index):
        """
        On tab close, remove subscript if tab is empty
        Reorder tab indices in autosave file to match
        current tab indices.
        TODO: currently, this only works when the button is clicked.
        Trigger it for the Ctrl+W shortcut as well.
        """
        root, subscripts = self.parsexml('subscript')

        found = False
        for s in subscripts:
            if not s.text:
                root.remove(s)
   
        self.writexml(root)