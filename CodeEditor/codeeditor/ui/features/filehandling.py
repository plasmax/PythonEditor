"""
Taken from Python Editor v0.1. Not yet implemented.
"""

import time
from codeeditor.utils.constants import AUTOSAVE_FILE
from codeeditor.ui.Qt import QtCore
from xml.etree import ElementTree

class FileHandler(QtCore.QObject):
    """
    Simple xml text storage.
    """
    def __init__(self, editor, path=None):
        self._path = (path if path else AUTOSAVE_FILE)
        self.editor = editor

        self.readautosave()
        editor.textChanged.connect(self.autosave) #document().modificationChanged is more sophisticated
    
    def readfile(self, path):
        """
        Opens any file and sets the editor's contents
        to the file's contents. Changes .pyc to .py in 
        path arguments.
        """
        path = path.replace('.pyc', '.py') #do not open compiled python files

        with open(file, 'r') as f:
            text = f.read()
        self.editor.setPlainText(text)

    def readautosave(self, path=None):
        """
        Sets editor text content. First checks the 
        autosave file for a <subscript> element with 
        a property that matches the path name provided. 
        If no path is provided (as on __init__), the 
        default autosave is read.
        """
        path = (path if path else self._path)

        parser = ElementTree.parse(AUTOSAVE_FILE)
        root = parser.getroot()
        subscripts = root.findall('subscript')

        path_list = [s.attrib.get('path') == path for s in subscripts]
        if not any(path_list):
            self.readfile(path)
            sub = ElementTree.Element('subscript')
            sub.attrib['path'] = path
            sub.attrib['date'] = time.asctime()
            root.append(sub)
            sub.text = self.editor.toPlainText()

            header = '<?xml version="1.0" encoding="UTF-8"?>'
            data = ElementTree.tostring(root)
            with open(AUTOSAVE_FILE, 'w') as f:
                f.write(header+data)

        for s in subscripts:
            if s.attrib.get('path') == path:
                self.editor.setPlainText(s.text)        

    @QtCore.Slot()
    def autosave(self):
        """
        Saves editor contents into autosave
        file with a path attribute and timestamp.
        """
        parser = ElementTree.parse(AUTOSAVE_FILE)
        root = parser.getroot()
        subscripts = root.findall('subscript')

        for s in subscripts:
            if s.attrib.get('path') == self._path:
                s.text = self.editor.toPlainText()
                s.attrib['date'] = time.asctime()

        header = '<?xml version="1.0" encoding="UTF-8"?>'
        data = ElementTree.tostring(root)
        with open(AUTOSAVE_FILE, 'w') as f:
            f.write(header+data) #all xml contents
