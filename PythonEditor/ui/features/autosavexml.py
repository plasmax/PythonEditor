from __future__ import unicode_literals
from __future__ import print_function
import os
import io
import unicodedata
from xml.etree import cElementTree as ElementTree
from PythonEditor.ui.Qt import QtCore, QtWidgets
from PythonEditor.utils import save
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


def parsexml(element_name, path=AUTOSAVE_FILE):
    if not create_autosave_file():
        return

    try:
        xmlp = ElementTree.XMLParser(encoding="utf-8")
        parser = ElementTree.parse(path, xmlp)
    except ElementTree.ParseError as e:
        print('ElementTree.ParseError', e)
        parser = fix_broken_xml(path)

    root = parser.getroot()
    elements = root.findall(element_name)
    return root, elements


def fix_broken_xml(path=AUTOSAVE_FILE):
    """
    Removes unwanted characters and
    (in case necessary in future
    implementations..) fixes other
    parsing errors with the xml file.
    """
    with io.open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    safe_string = remove_control_characters(content)

    with open(path, 'wt') as f:
        f.write(safe_string)

    xmlp = ElementTree.XMLParser(encoding="utf-8")
    parser = ElementTree.parse(path, xmlp)
    return parser


class AutoSaveManager(QtCore.QObject):
    """
    Simple xml text storage.

    TODO: Implement full design!
    # Reads when:
    - A new file is opened (text is set and file path is stored)
    - Restoring Autosave from XML: is read from xml file (unsaved)
    - Restoring Autosave from File: File is read from xml path
    when tab is left open

    # Writes when:
    - A file is saved (asks for file path if xml attrib not present)

    # Autosaves editor contents when:
    - An opened file (in read-only mode) has been edited
    - A new tab is opened and content created

    # Deletes when:
    - When writing to a file, the autosave text
    content is cleared, but the xml entry is left.
    - When closing a tab:
        if there is autosaved content:
            the user will be asked to save.
            if they do:
                the file is saved, the xml content cleared
        the xml entry will be deleted.
    """
    restore_tab_signal = QtCore.Signal(str)

    def __init__(self, tabs, tab_index=None):
        super(AutoSaveManager, self).__init__()
        self.setObjectName('AutoSaveManager')
        create_autosave_file()
        self.timer_waiting = False
        self.setup_save_timer(interval=1000)

        self.tabs = tabs
        self.setParent(tabs)

        # connect tab signals
        tss = tabs.tab_switched_signal
        tss.connect(self.tab_switch_handler)
        tss.connect(self.check_document_modified)
        tcr = tabs.tabCloseRequested
        tcr.connect(self.tab_close_handler)
        rts = tabs.reset_tab_signal
        rts.connect(self.clear_subscripts)
        cts = tabs.closed_tab_signal
        cts.connect(self.editor_close_handler)

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
        editor = self.tabs.currentWidget()
        hasedit = hasattr(self, 'editor')
        editorChanged = True if not hasedit else self.editor != editor
        isEditor = editor.objectName() == 'Editor'
        if isEditor and editorChanged:
            self.editor = editor
            self.connect_signals()

    def connect_signals(self):
        """ Connects signals to the current editor """
        self.editor.textChanged.connect(self.save_timer)
        self.editor.focus_in_signal.connect(self.check_document_modified)
        self.editor.contents_saved_signal.connect(self.handle_document_save)

    def disconnect_signals(self):
        """ Disconnects signals from the current editor """
        if not hasattr(self, 'editor'):
            return
        self.editor.textChanged.disconnect()
        self.editor.focus_in_signal.disconnect()
        self.editor.contents_saved_signal.disconnect()

    def setup_save_timer(self, interval=1000):
        """
        Initialise the autosave timer.
        :param interval: autosave interval in milliseconds
        :type interval: int
        """
        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(True)
        self.timer.setInterval(interval)
        self.timer.timeout.connect(self.autosave_handler)

    def save_timer(self):
        """
        On textChanged, if no text present, save immediately.
        Else, start a timer that will trigger autosave after
        a brief pause in typing.
        """
        if not self.editor.toPlainText().strip():
            return self.autosave()

        self.timer_waiting = True
        if self.timer.isActive():
            self.timer.stop()
        self.timer.start()

    def autosave_handler(self):
        """
        Autosave timeout triggers this.
        """
        self.timer_waiting = False
        self.autosave()

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

        with io.open(path, 'r') as f:
            text = f.read()

        self.editor.read_only = True

        # register the path on the editor object.
        # TODO: set this in the xml file!
        self.editor.path = path

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

        with io.open(path, 'wt', encoding='utf8', errors='ignore') as f:
            f.write(XML_HEADER+data)

    def readautosave(self):
        """
        Sets editor text content. First checks the
        autosave file for <subscript> elements and
        creates a tab per element.
        """
        root, subscripts = parsexml('subscript')

        editor_count = 0
        for s in subscripts:

            if not s.text:
                path = s.attrib.get('path')
                if path is None:
                    root.remove(s)
                    continue
                if not os.path.isfile(path):
                    continue
                s.attrib['name'] = os.path.basename(path)

            editor_count += 1

            try:
                tab_name = s.attrib['name']
            except KeyError:
                tab_name = None

            editor = self.tabs.new_tab(tab_name=tab_name)
            if 'uuid' in s.attrib:
                editor.uid = s.attrib['uuid']
            else:
                s.attrib['uuid'] = editor.uid

            if 'path' in s.attrib:
                editor.path = s.attrib['path']
            elif hasattr(editor, 'path'):
                s.attrib['path'] = editor.path

            if s.text:
                editor.setPlainText(s.text)
            else:
                self.editor = editor
                self.readfile(path)

        if editor_count == 0:
            self.tabs.new_tab()

        self.writexml(root)

    def check_document_modified(self):
        """
        On focus in event, check the xml
        to see if there are any differences.
        If there are, prompt the user to see
        if they want to update their tab.
        TODO: Display text/differences (difflib?)
        """
        if self.timer_waiting:
            return

        root, subscripts = parsexml('subscript')

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
        for index in range(self.tabs.count()):
            editor = self.tabs.widget(index)
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
                    index = self.tabs.currentIndex()
                    self.tabs.setTabText(index, name)
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
        file with a unique identifier (uuid)
        and accompanying file path if available.
        """
        root, subscripts = parsexml('subscript')

        found = False
        for s in subscripts:
            if s.attrib.get('uuid') == self.editor.uid:
                s.text = self.editor.toPlainText()
                s.attrib['name'] = self.editor.name
                if hasattr(self.editor, 'path'):
                    s.attrib['path'] = self.editor.path
                found = True

        if not found:
            sub = ElementTree.Element('subscript')
            sub.attrib['uuid'] = self.editor.uid
            sub.attrib['name'] = self.editor.name
            root.append(sub)
            sub.text = self.editor.toPlainText()

        self.writexml(root)

    @QtCore.Slot(object)
    def handle_document_save(self, editor):
        """
        Locate editor via uid attribute and remove the autosave
        contents if they match the given path file contents as
        these should be loaded from file on next app load
        (if the tab remains open).
        """
        if editor.read_only:
            return

        root, subscripts = parsexml('subscript')

        if not os.path.isfile(editor.path):
            print('No save file found. Retaining autosave.')
            return

        editor_found = False
        for s in subscripts:
            if s.attrib.get('uuid') == editor.uid:
                with open(editor.path, 'rt') as f:
                    if s.text == f.read():
                        editor_found = True
                        s.text = ''
                        s.attrib['path'] = editor.path
                    else:
                        msg = '{0} did not match {1} contents, retaining autosave'
                        print(msg.format(editor.name, editor.path))

        if editor_found:
            self.writexml(root)
            print('Document {0} should no longer have contents'.format(editor.uid))

    # @QtCore.Slot(str)
    # def check_editor_closed(self, uid):
    #     """
    #     Checks uid against all opened editors
    #     to confirm if editor has been closed. If it has,
    #     checks to see if an associated file text matches
    #     autosave, in which case it removes it.
    #     """
    #     # the hide signal gets called quite often,
    #     # so we limit it to one call per second
    #     if hasattr(self, 'last_hidden_uid'):
    #         if self.last_hidden_uid == uid:
    #             return

    #     timer = QtCore.QTimer()
    #     timer.setInterval(50)
    #     timer.setSingleShot(True)
    #     timer.timeout.connect(self.reset_last_hidden_uid)
    #     timer.start()
    #     self.last_hidden_uid = uid

    #     opened_editor_uids = []
    #     for i in range(self.tabs.count()):
    #         editor = self.tabs.widget(i)
    #         if hasattr(editor, 'uid'):
    #             opened_editor_uids.append(editor.uid)

    #     if uid in opened_editor_uids:
    #         return

    #     print(uid)

    # def reset_last_hidden_uid(self):
    #     print('resetting hidden uid')
    #     self.last_hidden_uid = None

    @QtCore.Slot(int)
    def tab_close_handler(self, tab_index):
        """
        Called on tabCloseRequested
        Note: if this slot is called via tabCloseRequested,
        the tab will have already been closed, so the tab_index
        will point to a different tab.
        """
        self.remove_empty()

    def remove_empty(self):
        """
        Remove subscripts if they are empty.
        """
        root, subscripts = parsexml('subscript')

        for s in subscripts:
            notext = not s.text
            nopath = s.attrib.get('path') is None
            if notext and nopath:
                root.remove(s)

        self.writexml(root)

    @QtCore.Slot(object)
    def editor_close_handler(self, editor):
        """
        Called on closed_tab_signal. Checks to see if contents
        have been saved (by checking the read_only state of the
        editor), then removes the autosave contents.
        """
        if not editor.read_only:
            msg_box = QtWidgets.QMessageBox()
            msg_box.setText('The document has been modified.')
            msg_box.setInformativeText('Do you want to save your changes?')
            buttons = msg_box.Save | msg_box.Discard# | msg_box.Cancel
            msg_box.setStandardButtons(buttons)
            msg_box.setDefaultButton(msg_box.Save)
            ret = msg_box.exec_()

            ## TODO: implement Cancel
            # if (ret == msg_box.Cancel):
            #     # restore the editor
            #     index = self.tabs.currentIndex()
            #     self.tabs.insertTab(index, editor, unicode(editor.name))
            #     return

            if (ret == msg_box.Save):
                path = save.save_as(editor)
                if path is None:
                    # user cancelled
                    return

                # we need to call this explicitly because the signal
                # would otherwise be executed after self.remove_saved
                self.handle_document_save(editor)

        self.remove_saved(uid=editor.uid)

    def remove_saved(self, uid=None):
        """
        Extra cleanup. Remove subscripts
        if they have an associated file
        whose text matches.
        """
        root, subscripts = parsexml('subscript')

        for s in subscripts:
            path = s.attrib.get('path')
            if path is None:
                continue
            if not os.path.isfile(path):
                continue
            if s.attrib.get('uuid') != uid:
                continue
            if not s.text:
                root.remove(s)

        self.writexml(root)

    @QtCore.Slot()
    def clear_subscripts(self):
        root, subscripts = parsexml('subscript')

        for s in subscripts:
            root.remove(s)

        self.writexml(root)
