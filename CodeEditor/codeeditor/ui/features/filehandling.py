"""
Taken from Python Editor v0.1. Not yet implemented.
"""

import time
from constants import AUTOSAVE_FILE
from xml.etree import ElementTree

class FileHandler(object):
    def __init__(self, editor):
        self._file = 'PythonEditorHistory.xml' # will need full path
        self.readautosave(self._file)
    
    def readfile(self, file):

        file = file.replace('.pyc', '.py') #do not open compiled python files

        with open(file, 'r') as f:
            text = f.read()
        self.editor.setPlainText(text)

    def readautosave(self, file):

        px = ElementTree.parse(AUTOSAVE_FILE)
        root = px.getroot()
        subscripts = root.findall('subscript')

        lzt = [s.attrib.get('path') == file for s in subscripts]
        if not any(lzt):
            self.readfile(file)
            sub = ElementTree.Element('subscript')
            sub.attrib['path'] = file
            sub.attrib['date'] = time.asctime()
            root.append(sub)
            sub.text = self.editor.toPlainText()

            header = '<?xml version="1.0" encoding="UTF-8"?>'
            data = ElementTree.tostring(root)
            with open(AUTOSAVE_FILE, 'w') as f:
                f.write(header+data)

        for s in subscripts:
            if s.attrib.get('path') == file:
                self.setPlainText(s.text)        

    def autosave(self):
        
        px = ElementTree.parse(AUTOSAVE_FILE)
        root = px.getroot()
        subscripts = root.findall('subscript')

        for s in subscripts:
            if s.attrib.get('path') == self._file:
                s.text = self.toPlainText()
                s.attrib['date'] = time.asctime()

        header = '<?xml version="1.0" encoding="UTF-8"?>'
        data = ElementTree.tostring(root)
        with open(AUTOSAVE_FILE, 'w') as f:
            f.write(header+data)
