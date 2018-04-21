from __future__ import unicode_literals
from __future__ import print_function
import unicodedata
from io import open
from xml.etree import cElementTree as ElementTree
from PythonEditor.ui.Qt import QtCore, QtWidgets
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
        tss.connect(self.check_document_modified)
        tcr = editortabs.tabCloseRequested
        tcr.connect(self.removeempty)

        self.set_editor()
        self.readautosave()

    @QtCore.Slot(int, int, bool)
    def tab_switch_handler(self, previous, current, tabremoved):
        if not tabremoved:  # nothing's been deleted
                            # so we need to disconnect
                            # signals from previous editor
            self.disconnect_signals()

        self.set_editor()

    def set_editor(self):
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
            self.connect_signals()

    def connect_signals(self):
        """ Connects signals to the give editor """
        self.editor.textChanged.connect(self.autosave)
        self.editor.focus_in_signal.connect(self.check_document_modified)

    def disconnect_signals(self):
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
            if 'uuid' in s.attrib:
                editor.uid = s.attrib['uuid']
            else:
                s.attrib['uuid'] = editor.uid
            editor.setPlainText(s.text)

        if editor_count == 0:
            self.editortabs.new_tab()

        self.writexml(root)

    def check_document_modified(self):
        """
        On focus in event, check the xml
        to see if there are any differences.
        If there are, prompt the user to see
        if they want to update their tab.
        TODO: Display text/differences (difflib?)
        """
        root, subscripts = self.parsexml('subscript')

        all_match = True
        not_matching = []
        for s in subscripts:
            if s.attrib.get('uuid') == self.editor.uid:
                if s.text is None:
                    continue

                editor_text = self.editor.toPlainText()
                text_match = (s.text == editor_text)

                editor_name = self.editor.name
                name_match = (s.attrib.get('name') == editor_name)

                if not (text_match and name_match):
                    all_match = False
                    not_matching.append((s, self.editor))

        if all_match:
            return

        editor_present = False
        for index in range(self.editortabs.count()):
            editor = self.editortabs.widget(index)
            for _, e in not_matching:
                if e == editor:
                    editor_present = True
                    break

        if not editor_present:
            return

        self.lock = True
        mismatch_count = len(not_matching)
        if mismatch_count != 1:
            count = str(mismatch_count)
            print('More than one mismatch! Found {0}'.format(count))
            for s in not_matching:
                uid = s.attrib.get('uuid')
                name = s.attrib.get('name')
                print(uid, name)

        for s, editor in not_matching:
            Yes = QtWidgets.QMessageBox.Yes
            No = QtWidgets.QMessageBox.No
            msg = 'Document "{0}" not matching'\
                  '\nPythonEditorHistory.xml "{1}"'\
                  '\n\nClick Yes to update this text to '\
                  'the saved version'\
                  '\nor No to overwrite the saved document.'

            name = s.attrib.get('name')
            msg = msg.format(editor.name, str(name))
            question = QtWidgets.QMessageBox.question
            reply = question(self.editor,
                             'Document Mismatch Warning',
                             msg,
                             Yes,
                             No)

            if reply == Yes:
                self.editor.setPlainText(s.text)
                if name is not None:
                    index = self.editortabs.currentIndex()
                    self.editortabs.setTabText(index, name)
            else:
                s.text = self.editor
                self.autosave()
        self.lock = True

        self._timer = QtCore.QTimer()
        self._timer.setInterval(500)
        self._timer.setSingleShot(True)

        def unlock(): self.lock = False
        self._timer.timeout.connect(unlock)
        self._timer.start()

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
