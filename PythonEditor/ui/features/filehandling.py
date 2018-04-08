import os
import time
from PythonEditor.utils.constants import AUTOSAVE_FILE
from PythonEditor.ui.Qt import QtCore, QtWidgets
from xml.etree import ElementTree

XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>'

class FileHandler(QtCore.QObject):
    """
    Simple xml text storage.
    """
    restore_tab_signal = QtCore.Signal(str)

    def __init__(self, editortabs, tab_index=None):
        super(FileHandler, self).__init__()
        if not os.path.isfile(AUTOSAVE_FILE):
            if not os.path.isdir(os.path.dirname(AUTOSAVE_FILE)):
                return
            else:
                with open(AUTOSAVE_FILE, 'w') as f:
                    f.write(XML_HEADER+'<script></script>')

        self.setObjectName('TabFileHandler')

        self.editortabs = editortabs
        self.setParent(editortabs)
        self.editortabs.widget_changed_signal.connect(self.setEditor)
        self.editortabs.tabCloseRequested.connect(self.removeempty) #document().modificationChanged is more sophisticated
        self.setEditor(editortabs.currentWidget())

        self.readautosave()

    @QtCore.Slot(QtWidgets.QPlainTextEdit)
    def setEditor(self, editor):
        """
        Sets the current editor
        and connects signals.
        """
        if hasattr(self, 'editor'):
            self.disconnectSignals()
        if editor is None:
            return
        if editor.objectName() == 'Editor':
            self.editor = editor
            self.connectSignals()

    def connectSignals(self):
        try:
            QtCore.Qt.UniqueConnection
        except AttributeError as e:
            print(e)
            QtCore.Qt.UniqueConnection = 128
        self.editor.textChanged.connect(self.autosave, QtCore.Qt.UniqueConnection) #document().modificationChanged is more sophisticated

    def disconnectSignals(self):

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

    def readautosave(self):
        """
        Sets editor text content. First checks the 
        autosave file for <subscript> elements and
        creates a tab per element.
        """
        parser = ElementTree.parse(AUTOSAVE_FILE)
        root = parser.getroot()
        subscripts = root.findall('subscript')

        for s in subscripts:
            if s.attrib.get('tab'):
                editor = self.editortabs.new_tab()#TODO should assign a UUID 
                editor.setPlainText(s.text)

    @QtCore.Slot()
    def autosave(self):
        """
        Saves editor contents into autosave
        file with a path attribute and timestamp.
        """
        parser = ElementTree.parse(AUTOSAVE_FILE)
        root = parser.getroot()
        subscripts = root.findall('subscript')

        tab_index = str(self.editortabs.currentIndex())
        found = False
        for s in subscripts:
            if s.attrib.get('tab') == tab_index:
                s.text = self.editor.toPlainText()
                found = True

        if not found:
            sub = ElementTree.Element('subscript')
            sub.attrib['tab'] = tab_index
            root.append(sub)
            sub.text = self.editor.toPlainText()
   
        data = ElementTree.tostring(root)
        with open(AUTOSAVE_FILE, 'w') as f:
            f.write(XML_HEADER+data) #all xml contents

    @QtCore.Slot(int)
    def removeempty(self, tab_index):
        parser = ElementTree.parse(AUTOSAVE_FILE)
        root = parser.getroot()
        subscripts = root.findall('subscript')

        tab_index = str(self.editortabs.currentIndex())
        found = False
        for s in subscripts:
            # if s.attrib.get('tab') == tab_index:
            if s.text.strip() == '':
                root.remove(s)
