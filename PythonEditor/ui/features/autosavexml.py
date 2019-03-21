"""
All modifications to the PythonEditor.xml
file are done through this module.

All the out points of this module:
- line 62 in init_file_header
"""

from __future__ import unicode_literals
from __future__ import print_function

import os
import io
import unicodedata
import warnings
import tempfile
import difflib
from xml.etree import cElementTree as ElementTree

from PythonEditor.ui.Qt import QtCore, QtWidgets
from PythonEditor.ui import editor
from PythonEditor.utils.signals import connect
from PythonEditor.utils.debug import debug
from PythonEditor.utils.constants import NUKE_DIR


AUTOSAVE_FILE = os.path.join(NUKE_DIR, 'PythonEditorHistory.xml')
XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>'


class AutoSaveManager(QtCore.QObject):
    """
    Simple xml text storage.

    TODO: Check that these rules are being followed.
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
    def __init__(self, tabs, tab_index=None):
        super(AutoSaveManager, self).__init__()

        try:
            create_autosave_file()
        except CouldNotCreateAutosave:
            warnings.warn('Could not create autosave.')
            return None

        self.setObjectName('AutoSaveManager')
        self.autosave_timer_waiting = False
        self.setup_save_timer(interval=1000) # TODO: hook this up

        self.tabeditor = tabs
        self.editor = tabs.editor
        self.tabs = tabs.tabs
        self.setParent(tabs)

        self.readautosave()
        self.connect_signals()

    def connect_signals(self):
        """ Connects the editor and tab signals to this class """
        pairs = [
            (self.editor.text_changed_signal, self.save_timer),
            (self.editor.focus_in_signal, self.check_autosave_modified),
        ]
        self._connections = []
        for signal, slot in pairs:
            name, _, handle = connect(self.editor, signal, slot)
            self._connections.append((name, slot))

        # connect tab signals
        tabs = self.tabs
        cts = tabs.tab_close_signal
        cts.connect(self.remove_subscript)
        trs = tabs.tab_renamed_signal
        trs.connect(self.save_by_uuid)
        tmv = tabs.tab_repositioned_signal
        tmv.connect(self.update_tab_index)
        tcc = tabs.currentChanged
        tcc.connect(self.store_current_index)
        tss = self.tabeditor.tab_switched_signal
        tss.connect(self.check_autosave_modified)
        css = tabs.contents_saved_signal
        css.connect(self.handle_document_save)
        rts = tabs.reset_tab_signal
        rts.connect(self.clear_subscripts)

    def setup_save_timer(self, interval=500):
        """
        Initialise the autosave timer.
        :param interval: autosave interval in milliseconds
        :type interval: int
        """
        self.autosave_timer = QtCore.QTimer()
        self.autosave_timer.setSingleShot(True)
        self.autosave_timer.setInterval(interval)

    def save_timer(self):
        """
        On text_changed_signal, if no text present, save immediately.
        Else, start a timer that will trigger autosave after
        a brief pause in typing.
        """

        # why did I used to block saving when no text was present?
        # maybe because a timer is unecessary...
        # if not self.editor.toPlainText().strip():
        #     return self.autosave()

        self.autosave_timer_waiting = True
        if self.autosave_timer.isActive():
            self.autosave_timer.stop()

        self.setup_save_timer()
        self.autosave_timer.timeout.connect(self.autosave_handler)
        self.autosave_timer.start()

    def autosave_handler(self):
        """
        Autosave timeout triggers this.
        """
        self.autosave_timer_waiting = False
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

        self.editor.path = path
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

        TODO: Would be nice to remember current tab
        (alongside preferences) when reading autosave.
        """
        root, subscripts = parsexml('subscript')
        if len(subscripts) == 0:
            return
        subscripts = sorted(
            subscripts,
            key=get_element_tab_index
        )

        autosaves = []
        i = 0
        for s in subscripts:
            name = s.attrib.get('name')
            if name is None:
                continue
            autosaves.append((i, s))
            i += 1

        standard_tabs = False
        draw_own_close_btn = True
        draw_own_tab = False
        # storing autosave into new tabs
        for i, s in autosaves:
            name = s.attrib.get('name')
            data = s.attrib.copy()

            # if there's no text saved,
            # but there is a path, try and
            # get the file contents
            if not s.text:
                path = s.attrib.get('path')
                if path is not None:
                    if os.path.isfile(path):
                        with open(path, 'r') as f:
                            data['text'] = f.read()

            data['text'] = s.text

            if standard_tabs:
                self.tabs.new_tab(tab_name=name)
            elif draw_own_close_btn:
                # tab_name = name+' '*5
                tab_name = name
                self.tabs.new_tab(tab_name=tab_name, tab_data=data) # hax for enough space for close button :'(
            elif draw_own_tab:
                tab_name = name+' '*5
                self.tabs.new_tab(tab_name=' '*len(tab_name))

            path = data.get('path')
            if path is not None:
                self.tabs.setTabToolTip(i, path) # and if this changes?


        # try and get the index of the current tab from the last session
        index = self.tabs.count()
        root, index_elements = parsexml('current_index')
        for index_element in index_elements:
            current_index = int(index_element.text)
            out_of_range = -1 < index < self.tabs.count()
            if not out_of_range:
                index = current_index

        # set tab and editor contents.
        self.tabs.setCurrentIndex(index)
        self.tabeditor.set_editor_contents(index)

    def read_current_tab_file(self):
        """
        Reads the file contents from the current tab's
        linked file and sets the editor contents to that
        file's contents.
        """
        path = self.tabs.get('path')
        if path is None:
            return
        if not os.path.isfile(path):
            # set tab saved status to false
            data = self.tabs.tabData(index)
            if data is None:
                return
            data['saved'] = False
            self.tabs.setTabData(index, data)
            return
        with open(path, 'r') as f:
            text = f.read()
        self.editor.setPlainText(text)
        self.tabs['text'] = text
        self.tabs['saved'] = True

    def check_document_modified(self, index=-1, path=''):
        """
        For tabs that have an associated path, check that the
        text matches the file contents the path's pointing at.
        """
        if not path:
            return
        if index == -1:
            return
        if index > self.tabs.count():
            return
        if index != self.tabs.currentIndex():
            return
        if not os.path.isfile(path):
            # set tab saved status to false
            # data = self.tabs.tabData(index)
            # if data is None:
            #     return
            # data['saved'] = False
            # self.tabs.setTabData(index, data)
            self.tabs['saved'] = False
            return
        with open(path, 'r') as f:
            text = f.read()

        editor_text = self.editor.toPlainText()
        if text == editor_text:
            return

        # TODO:
        """
        I think that instead of a popup window I'd rather
        display the state of the tab in an obvious way and let
        the user see a diff if they request one through a right-click menu.
        """
        self.tabs['saved'] = False

#         self.lock = True
#         l1 = text.splitlines(True)
#         l2 = editor_text.splitlines(True)

#         ctx_diff = difflib.context_diff(l1, l2)
#         diff_text = ''
#         for i in ctx_diff:
#             diff_text += i

#         name = self.tabs.tabText(index)
#         msg = '%s (tab "%s") has changed on disk. Reload?' % (path, name)
#         msgbox = QtWidgets.QMessageBox()
#         msgbox.setText(msg)
#         msgbox.setInformativeText("""
# Click Reload to load the file on disk and replace the text in the editor.
# Click Ignore to temporarily ignore this message.
# """
#         )
#         reload_button = QtWidgets.QPushButton('Reload')
#         msgbox.addButton(reload_button, QtWidgets.QMessageBox.ActionRole)

#         layout = QtWidgets.QVBoxLayout()
#         lm = msgbox.layout()
#         lm.addLayout(layout, lm.rowCount(), lm.columnCount())
#         diff_button = QtWidgets.QPushButton('Show Diff')
#         layout.addWidget(diff_button)
#         diff_editor = editor.Editor()
#         diff_editor.setPlainText(diff_text)
#         # diff_editor.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
#         from functools import partial
#         add_de = partial(layout.addWidget, diff_editor)
#         diff_button.clicked.connect(add_de)
#         msgbox.setStandardButtons(
#             QtWidgets.QMessageBox.Ignore
#         )
#         msgbox.setDefaultButton(QtWidgets.QMessageBox.Ignore)
#         ret = msgbox.exec_()

#         if msgbox.clickedButton() == reload_button:
#             self.read_current_tab_file()
#         elif ret == QtWidgets.QMessageBox.Ignore:
#             # TODO: disassociate file from saved file
#             pass

#         QtCore.QTimer.singleShot(1500, self.unlock)

    lock = False
    def check_autosave_modified(self, index=-1):
        """
        On focus in event, check the xml (or
        the saved file if present) to see if
        there are any differences. If there
        are, ask the user if they want to update
        their tab.
        """

        if self.lock:
            # don't allow this to be called again before
            # autosave is complete.
            return

        # FIXME: This will change when
        # autocompletion goes synchronous.
        if self.editor._key_pressed:
            return

        # first check against saved files,
        # which will autosave before continuing.
        self.check_document_modified(
            self.tabs.currentIndex(),
            self.tabs.get('path')
        )

        root, subscripts = parsexml('subscript')

        tabs = self.tabs
        if self.tabs.currentIndex() == -1:
            return
        tab_uid = tabs['uuid']
        editor_text = self.editor.toPlainText()

        # find all subscripts with a
        # matching uid for our current tab
        all_match = True
        not_matching = []
        for s in subscripts:
            if s.text is None:
                continue
            uid = s.attrib.get('uuid')
            if uid != tab_uid:
                continue

            text_match = (s.text == editor_text)
            name_match = (s.attrib.get('name') == tabs['name'])

            if not all([text_match, name_match]):
                all_match = False
                not_matching.append((s, uid))

        if all_match:
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

        for s, uid in not_matching:
            # TODO: Display text/differences (difflib?)
            Yes = QtWidgets.QMessageBox.Yes
            No = QtWidgets.QMessageBox.No
            msg = 'Document "{0}" not matching'\
                  '\nPythonEditorHistory.xml "{1}"'\
                  '\n\nClick Yes to update this text to '\
                  'the saved version'\
                  '\nor No to overwrite the saved document.'

            name = s.attrib.get('name')
            msg = msg.format(tabs['name'], str(name))
            ask = QtWidgets.QMessageBox.question
            title = 'Load Autosave?'
            reply = ask(self.editor, title, msg, Yes, No)
            if reply == Yes:
                self.editor.setPlainText(s.text)
                self.tabs['text'] = s.text
                if name is not None:
                    index = self.tabs.currentIndex()
                    self.tabs.setTabText(index, name)
            elif reply == No:
                text = self.editor.toPlainText()
                s.text = text
                self.tabs['text'] = text
                self.autosave()

        # give the autosave 1500ms to complete
        # before allowing comparison checks again
        QtCore.QTimer.singleShot(1500, self.unlock)

    def unlock(self):
        self.lock = False

    def sync_tab_indices(self):
        """
        Synchronise the tab_index saved in <subscript>
        elements and the tab indices of all tabs in the QTabBar.
        """
        root, subscripts = parsexml('subscript')
        for i in range(self.tabs.count()):
            data = self.tabs.tabData(i)
            for s in subscripts:
                if s.attrib.get('uuid') != data['uuid']:
                    continue
                s.attrib['tab_index'] = str(i)
                break
        writexml(root)

    @QtCore.Slot()
    def autosave(self):
        """
        Saves editor contents into autosave
        file with a unique identifier (uuid)
        and accompanying file path if available.
        """
        tabs = self.tabs
        self.save_by_uuid(
            tabs['uuid'],
            tabs['name'],
            tabs['text'],
            str(tabs.currentIndex()),
            tabs.get('path')
            )
        self.sync_tab_indices()

    @QtCore.Slot(str, str, str, str, object)
    def save_by_uuid(self, uid, name, text, index, path=None):
        """
        Only update a specific subscript given by uuid.
        """
        root, subscripts = parsexml('subscript')

        found = False
        for s in subscripts:
            if s.attrib.get('uuid') == uid:
                found = True
                sub = s
                break
        else:
            sub = ElementTree.Element('subscript')
            root.append(sub)

        sub.attrib['uuid'] = uid
        sub.attrib['name'] = name
        sub.text = text
        sub.attrib['tab_index'] = index

        if path is not None:
            sub.attrib['path'] = path

        writexml(root)

    def store_current_index(self):
        """
        TODO: store a <currentindex> element
        and then set the currentindex on readautosave (if present! backwards compat).
        """
        root, index_elements = parsexml('current_index')
        if len(index_elements) == 0:
            ci = ElementTree.Element('current_index')
            root.append(ci)
        else:
            ci = index_elements[0]
        ci.text = str(self.tabs.currentIndex())
        writexml(root)

    @QtCore.Slot(int, int)
    def update_tab_index(self, from_index, to_index):
        # return # I want to do this threaded.
        for i in from_index, to_index:
            data = self.tabs.tabData(i)
            if data is None:
                return
            data['tab_index'] = i
            self.tabs.setTabData(i, data) # don't like that we'e modifying tabdata here...
            self.save_by_uuid(
                data['uuid'],
                data['name'],
                data['text'],
                str(i),
                data.get('path')
                )
        self.store_current_index()
        self.sync_tab_indices()

    @QtCore.Slot(object)
    def handle_document_save(self, uid):
        """
        Locate tab via uid attribute and remove the autosave
        contents if they match the given path file contents as
        these should be loaded from file on next app load
        (if the tab remains open).
        """

        index = -1
        if self.tabs['uuid'] != uid:
            for i in range(self.tabs.count()):
                data = self.tabs.tabData(i)
                if data.get('uuid') != uid:
                    continue
                index = i
                break
            else:
                return
        else:
            index = self.tabs.currentIndex()

        data = self.tabs.tabData(index)
        path = data.get('path')
        if path is None:
            return
        if not os.path.isfile(path):
            print('No save file found at %s. Retaining autosave.' % path)
            return

        with open(path, 'rt') as f:
            contents = f.read()

        root, subscripts = parsexml('subscript')
        for s in subscripts:

            if s.attrib.get('uuid') != uid:
                continue

            if s.text != contents:
                msg = '{0} did not match {1} contents, autosave'
                debug(msg.format(name, path))
                return

            s.attrib['path'] = path
            self.tabs['saved'] = True
            # FIXME: i think it would be better to keep a temp copy of all open files
            # until they are closed.
            writexml(root)

    @QtCore.Slot(object, int)
    def handle_tab_moved(self, editor, tab_index):
        self.autosave()

    @QtCore.Slot(int)
    def handle_tab_close(self, tab_index):
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

        writexml(root)

    @QtCore.Slot(str)
    def remove_subscript(self, uid):
        """
        Explicitly remove a subscript entry.

        If we arrive here it means one of the following:
        a) file is not open for editing (read-only)
        b) we've already saved
        c) we've discarded the document
        So it's safe to remove it.

        :param uid: Unique Identifier of subscript
        to remove
        """
        root, subscripts = parsexml('subscript')

        item_removed = False
        for s in subscripts:
            if s.attrib.get('uuid') == uid:
                root.remove(s)
                item_removed = True

        if item_removed:
            writexml(root)

    @QtCore.Slot()
    def clear_subscripts(self):
        """
        Remove all subscripts.
        """
        root, subscripts = parsexml('subscript')

        for s in subscripts:
            root.remove(s)

        writexml(root)



class CouldNotCreateAutosave(Exception):
    pass


def create_autosave_file():
    """
    Create the autosave file into which
    PythonEditor stores all tab contents.
    """
    # look for the autosave
    if os.path.isfile(AUTOSAVE_FILE):

        # if the autosave file is empty, write header
        with open(AUTOSAVE_FILE, 'r') as f:
            is_empty = not bool(f.read().strip())
        if is_empty:
            init_file_header()
    else:

        # if file not found, check if directory exists
        if not os.path.isdir(NUKE_DIR):
            # filehandle, filepath = tempfile.mkstemp()
            # msg = 'Directory %s does not exist, saving to %s' % (NUKE_DIR, filepath)
            msg = 'Directory %s does not exist' % NUKE_DIR
            # NUKE_DIR = filepath
            raise CouldNotCreateAutosave(msg)
        else:
            init_file_header()
    return True


def init_file_header():
    """
    Write the default file header into the xml file.
    Overwrites any existing file.
    """
    with open(AUTOSAVE_FILE, 'w') as f:
        f.write(XML_HEADER+'<script></script>')


def get_editor_xml():
    if not create_autosave_file():
        return
    parser = ElementTree.parse(AUTOSAVE_FILE)
    root = parser.getroot()
    editor_elements = root.findall('external_editor_path')
    return root, editor_elements


def get_external_editor_path():
    """
    Checks the autosave file for an
    <external_editor_path> element.
    """
    editor_path = os.environ.get('EXTERNAL_EDITOR_PATH')
    if (editor_path is not None
            and os.path.isdir(os.path.dirname(editor_path))):
        return editor_path

    root, editor_elements = get_editor_xml()

    if editor_elements:
        editor_element = editor_elements[0]
        path = editor_element.text
        if path and os.path.isdir(os.path.dirname(path)):
            editor_path = path

    if editor_path:
        os.environ['EXTERNAL_EDITOR_PATH'] = editor_path
        return editor_path
    else:
        return set_external_editor_path(ask_user=True)


def set_external_editor_path(path=None, ask_user=False):
    """
    Prompts the user for a new
    external editor path.
    TODO: Set temp program if none found.
    """
    root, editor_elements = get_editor_xml()
    for e in editor_elements:
        root.remove(e)

    if ask_user and not path:
        from PythonEditor.ui.Qt import QtWidgets
        dialog = QtWidgets.QInputDialog()
        args = (dialog,
                u'Get Editor Path',
                u'Path to external text editor:')
        results = QtWidgets.QInputDialog.getText(*args)
        path, ok = results
        if not ok:
            msg = 'Certain features will not work without '\
                'an external editor. \nYou can add or change '\
                'an external editor path later in Edit > Preferences.'
            msgBox = QtWidgets.QMessageBox()
            msgBox.setText(msg)
            msgBox.exec_()
            return None

    if path and os.path.isdir(os.path.dirname(path)):
        editor_path = path
        os.environ['EXTERNAL_EDITOR_PATH'] = editor_path

        element = ElementTree.Element('external_editor_path')
        element.text = path
        root.append(element)

        writexml(root)
        return path

    elif ask_user:
        from PythonEditor.ui.Qt import QtWidgets
        msg = u'External editor not found. '\
              'Certain features will not work.'\
              '\nYou can add or change an external '\
              'editor path later in Edit > Preferences.'
        msgBox = QtWidgets.QMessageBox()
        msgBox.setText(msg)
        msgBox.exec_()
        return None


def not_ctrl(ch):
    is_ctrl_char = unicodedata.category(ch) == 'Cc'
    not_newline = ch != '\n'
    return (is_ctrl_char and not_newline)


def remove_control_characters(s):
    """
    Identify and remove any control characters from given string s.
    """
    cc = ''.join(ch for ch in s if not_ctrl(ch))
    print('Removing undesirable control characters:', cc)

    def no_cc(ch):
        if ch == '\n':
            return True
        if unicodedata.category(ch) != "Cc":
            return True
        return False

    return ''.join(ch for ch in s if no_cc(ch))


def parsexml(element_name, path=AUTOSAVE_FILE):
    """
    Retrieve the root and a list of <element_name>
    elements from a given xml file.
    """
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


def writexml(root, path=AUTOSAVE_FILE):
    data = ElementTree.tostring(root)
    data = data.decode('utf-8')
    data = data.replace('><subscript', '>\n<subscript')
    data = data.replace('</subscript><', '</subscript>\n<')

    with io.open(path, 'wt', encoding='utf8', errors='ignore') as f:
        f.write(XML_HEADER+data)


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
    try:
        parser = ElementTree.parse(path, xmlp)
    except ElementTree.ParseError:
        print('Fatal Error with xml structure. A backup of your autosave has been made.')
        backup_autosave_file(path, content)
        init_file_header()
        xmlp = ElementTree.XMLParser(encoding="utf-8")
        parser = ElementTree.parse(path, xmlp)
        print(parser)
    return parser


def backup_autosave_file(path, content):
    handle, temp_path = tempfile.mkstemp()
    with open(temp_path, 'w') as f:
        f.write(content)
    print('A backup of %s has been saved here: %s' % (path, temp_path))


def remove_empty_autosaves():
    """
    Clean autosave file of subscripts with no
    information (no text and invalid or absent path).
    """
    root, subscripts = parsexml('subscript')
    for s in subscripts:
        if not s.text:
            path = s.attrib.get('path')
            if path is None:
                root.remove(s)
                continue
            if not os.path.isfile(path):
                root.remove(s)
                continue
            s.attrib['name'] = os.path.basename(path)
    writexml(root)


def get_element_tab_index(subscript):
    """
    Helper function that returns the
    tab_index attribute of an xml element
    or 1 if none is found.
    """
    tab_index = subscript.attrib.get('tab_index')
    try:
        return int(tab_index)
    except TypeError, ValueError:
        return 1
