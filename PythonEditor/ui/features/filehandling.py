from __future__ import unicode_literals
from __future__ import print_function
import unicodedata
from io import open
from xml.etree import ElementTree
from PythonEditor.ui.Qt import QtCore
from PythonEditor.utils.constants import (AUTOSAVE_FILE,
                                          XML_HEADER,
                                          create_autosave_file)


def remove_control_characters(s):
    def notCtrl(ch): return unicodedata.category(ch) == "Cc" and ch != '\n'
    cc = "".join(ch for ch in s if notCtrl(ch))
    print('Removing undesirable control characters:', cc)

    def no_cc(ch):
        if ch == '\n':
            return True
        if unicodedata.category(ch) != "Cc":
            return True
        return False

    return "".join(ch for ch in s if no_cc(ch))


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

        # connect tab signals
        tss = editortabs.tab_switched_signal
        tss.connect(self.tab_switch_handler)
        tcr = editortabs.tabCloseRequested
        tcr.connect(self.removeempty)

        self.setEditor()
        self.readautosave()

    @QtCore.Slot(int, int, bool)
    def tab_switch_handler(self, previous, current, tabremoved):
        if not tabremoved:  # nothing's been deleted
                            # so we need to disconnect
                            # signals from previous editor
            self.disconnectSignals()

        self.setEditor()

    def setEditor(self):
        """
        Sets the current editor
        and connects signals.
        """
        editor = self.editortabs.currentWidget()
        hasedit = hasattr(self, 'editor')
        editorChanged = True if not hasedit else self.editor != editor
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
        self.editor.textChanged.connect(self.autosave)
        self.editor.focus_in_signal.connect(self.check_document_modified)
        # document().modificationChanged ?

    def disconnectSignals(self):
        if not hasattr(self, 'editor'):
            return
        self.editor.textChanged.disconnect()
        self.editor.focus_in_signal.disconnect()

    def readfile(self, path):
        """
        Opens any file and sets the editor's contents
        to the file's contents. Changes .pyc to .py in
        path arguments.
        """
        if '.xml' in path:
            return self.readxml(path)

        # do not open compiled python files
        path = path.replace('.pyc', '.py')

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
        data = data.replace('><subscript', '>\n<subscript')
        data = data.replace('</subscript><', '</subscript>\n<')
        with open(path, 'wt', encoding='utf8', errors='ignore') as f:
            f.write(XML_HEADER+data)

    def parsexml(self, element_name, path=AUTOSAVE_FILE):
        if not create_autosave_file():
            return

        try:
            xmlp = ElementTree.XMLParser(encoding="utf-8")
            parser = ElementTree.parse(path, xmlp)
        except ElementTree.ParseError as e:
            print('ElementTree.ParseError', e)
            parser = self.fix_broken_xml(path)

        root = parser.getroot()
        elements = root.findall(element_name)
        return root, elements

    def fix_broken_xml(self, path):
        """
        Removes unwanted characters and
        (in case necessary in future
        implementations..) fixes other
        parsing errors with the xml file.
        """
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        safe_string = remove_control_characters(content)

        with open(path, 'wt') as f:
            f.write(safe_string)

        xmlp = ElementTree.XMLParser(encoding="utf-8")
        parser = ElementTree.parse(path, xmlp)
        return parser

    def check_document_modified(self):
        """
        On focus in event, check the xml
        to see if there are any differences.
        If there are, prompt the user to see
        if they want to update their tab.
        """
        pass  # TODO: implement this!

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

            try:
                tab_name = s.attrib['name']
            except KeyError:
                tab_name = None

            editor = self.editortabs.new_tab(tab_name=tab_name)
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

        found = False
        for s in subscripts:
            if s.attrib.get('uuid') == self.editor.uid:
                s.text = self.editor.toPlainText()
                s.attrib['name'] = self.editor.name
                found = True

        if not found:
            sub = ElementTree.Element('subscript')
            sub.attrib['uuid'] = self.editor.uid
            sub.attrib['name'] = self.editor.name
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

        for s in subscripts:
            if not s.text:
                root.remove(s)

        self.writexml(root)
