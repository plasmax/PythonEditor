"""
All modifications to the PythonEditor.xml
file are done through this module.

Functions that write to the autosave file:
- create_empty_autosave
- writexml
- fix_broken_xml
"""
from __future__ import unicode_literals
from __future__ import print_function

import os
import io
import unicodedata
import warnings
import tempfile
import difflib
from functools import partial
from xml.etree import cElementTree as ETree

from PythonEditor.ui.Qt import QtCore, QtWidgets
from PythonEditor.ui import editor
from PythonEditor.utils.signals import connect
from PythonEditor.utils.debug import debug
from PythonEditor.utils.constants import NUKE_DIR


def is_file(path):
    """ Safe is_file.
    """
    try:
        return os.path.isfile(path)
    except Exception:
        return False


def parent_isdir(file_path):
    return os.path.isdir(
    os.path.dirname(file_path)
    )


def haspermissions(path):
    return os.access(
        path,
        os.R_OK|os.W_OK
    )


def define_autosave_path():
    """ Allow users to define a custom
    xml file path via an environment
    variable.
    """
    global NUKE_DIR
    global AUTOSAVE_FILE
    AUTOSAVE_FILE = os.getenv(
        'PYTHONEDITOR_AUTOSAVE_FILE'
    )
    if (AUTOSAVE_FILE is None
        or not parent_isdir(AUTOSAVE_FILE)
        ):
        if not os.path.isdir(NUKE_DIR):
            NUKE_DIR = os.path.expanduser('~')
        AUTOSAVE_FILE = os.path.join(
            NUKE_DIR,
            'PythonEditorHistory.xml'
        )
    os.environ[
        'PYTHONEDITOR_AUTOSAVE_FILE'
    ] = AUTOSAVE_FILE
    return AUTOSAVE_FILE


AUTOSAVE_FILE = define_autosave_path()
XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>'


class AutoSaveManager(QtCore.QObject):
    """
    Simple xml text storage.

    TODO: Test that these rules are being followed.
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
        self.setup_save_timer(interval=1000)

        self.tabeditor = tabs
        self.editor = tabs.editor
        self.tabs = tabs.tabs
        self.setParent(tabs)

        self.readautosave()
        self.connect_signals()

    def connect_signals(self):
        """ Connects the editor, tabeditor
        and tab signals to this class
        """
        editor = self.editor
        editor.text_changed_signal.connect(
            self.save_timer)
        editor.focus_in_signal.connect(
            self.check_autosave_modified)

        tabs = self.tabs
        tabs.tab_close_signal.connect(
            self.remove_subscript
        )
        tabs.tab_renamed_signal.connect(
            self.save_by_uuid
        )
        tabs.tab_repositioned_signal.connect(
            self.update_tab_index
        )
        tabs.currentChanged.connect(
            self.store_current_index
        )
        tabs.contents_saved_signal.connect(
            self.handle_document_save
        )
        tabs.reset_tab_signal.connect(
            self.clear_subscripts
        )

        tabeditor = self.tabeditor
        tabeditor.tab_switched_signal.connect(
            self.check_autosave_modified
        )

    def save_timer(self):
        """ On text_changed_signal, if no text present, save immediately.
        Else, start a timer that will trigger autosave after
        a brief pause in typing.
        """
        # FIXME: so this was set up to allow quick clearing of
        # documents so that the tab could be closed immediately
        # afterwards. however, it caused a problem somewhere so
        # was commented out. I don't remember where.
        # if not self.editor.toPlainText().strip():
        #     return self.autosave()

        self.autosave_timer_waiting = True
        if self.autosave_timer.isActive():
            self.autosave_timer.stop()

        self.setup_save_timer()
        self.autosave_timer.timeout.connect(self.autosave_handler)
        if self.editor.document().isModified():
            self.autosave_timer.start()

    def setup_save_timer(self, interval=500):
        """ Initialise the autosave timer.
        :param interval: autosave interval in milliseconds
        :type interval: int
        """
        self.autosave_timer = QtCore.QTimer()
        self.autosave_timer.setSingleShot(True)
        self.autosave_timer.setInterval(interval)

    def autosave_handler(self):
        """ Autosave timeout triggers this.
        """
        self.autosave_timer_waiting = False
        if self.editor.document().isModified():
            self.autosave()

    def readautosave(self):
        """ Sets editor text content. First checks the
        autosave file for <subscript> elements and
        creates a tab per element.
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

            data['text'] = s.text
            # if there's no text saved,
            # but there is a path, try and
            # get the file contents
            if not s.text:
                path = s.attrib.get('path')
                if is_file(path):
                    with open(path, 'r') as f:
                        data['text'] = f.read()

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
        index = self.tabs.count()-1
        root, index_elements = parsexml('current_index')
        for index_element in index_elements:
            current_index = int(index_element.text)
            if current_index in range(0, index):
                index = current_index
                break

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

    def check_autosave_modified(self):
        """
        On focus in event, check the xml (or
        the saved file if present) to see if
        there are any differences. If there
        are, ask the user if they want to update
        their tab.
        """
        # remove any popup windows that
        # were previously showing
        self.remove_existing_popups(
            'Document out of sync warning'
        )

        # first check against saved files,
        self.check_document_modified(
            self.tabs.currentIndex(),
            self.tabs.get('path')
        )

        # safety: do not autosave if current
        # index is -1. this should not happen
        # as there is no [+] tab anymore.
        tabs = self.tabs
        if tabs.currentIndex() == -1:
            return

        # read the autosave file
        root, subscripts = parsexml('subscript')

        # sync tab names from the autosave
        tab_uid = tabs['uuid']
        for s in subscripts:
            uid = s.attrib.get('uuid')
            if uid != tab_uid:
                continue
            xml_tab_name = s.attrib.get('name')
            if xml_tab_name == tabs['name']:
                continue
            index = self.tabs.currentIndex()
            self.tabs.setTabText(index, xml_tab_name)
            self.tabs['name'] = xml_tab_name

        # find all subscripts with a
        # matching uid for our current tab
        not_matching = []
        editor_text = self.editor.toPlainText()
        for s in subscripts:
            if s.text is None:
                continue
            uid = s.attrib.get('uuid')
            if uid != tab_uid:
                continue
            if s.text != editor_text:
                not_matching.append((s, uid))

        mismatch_count = len(not_matching)
        if mismatch_count == 0:
            return
        # print('number of mismatches:',mismatch_count,not_matching)

        # if there's more than one subscript with
        # the same uid as the current tab, something
        # has gone wrong.
        if mismatch_count != 1:
            count = str(mismatch_count)
            print('More than one mismatch! Found {0}'.format(count))
            for s in not_matching:
                uid = s.attrib.get('uuid')
                name = s.attrib.get('name')
                print(uid, name)

        for s, uid in not_matching:
            self.show_diff_text_popup(s)

    def check_document_modified(self, index=-1, path=''):
        """
        For tabs that have an associated path,
        check that the text matches the file
        contents the path is pointing at, and
        set the tab saved status to False if
        it does not match.
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
            self.tabs['saved'] = False
            return
        with open(path, 'r') as f:
            text = f.read()

        editor_text = self.editor.toPlainText()
        if text == editor_text:
            return

        self.tabs['saved'] = False

    def show_diff_text_popup(self, subscript):
        popup_bar = QtWidgets.QWidget()
        self.popup_bar = popup_bar
        name = 'Document out of sync warning'
        popup_bar.setObjectName(name)
        popup_bar.setLayout(
            QtWidgets.QHBoxLayout(popup_bar)
        )

        label = QtWidgets.QLabel()
        label.setText(
            'This tab is out of sync\n'\
            'with the autosave.'
        )
        popup_bar.layout().addWidget(label)

        B = QtWidgets.QPushButton
        new_button    = B('Load into New Tab')
        new_button.setToolTip(
            'Click to load the text inside '\
            'the editor into a fresh tab, '\
            'updating the autosaved version '\
            'into the previous tab.'
        )
        save_button   = B('Save This Version')
        save_button.setToolTip(
            'Click to choose this version '\
            'as the version to save.'
        )
        update_button = B('Update From Autosave')
        update_button.setToolTip(
            'Load the version from the '\
            'autosave into this tab.'
        )

        diff_button   = B('Show Diff')
        diff_button.setToolTip(
            'Show the difference between the two.'
        )

        remove = partial(
            self.remove_existing_popups,
            name
        )

        layout = self.tabeditor.layout()
        layout.insertWidget(1, popup_bar)

        stylesheet = """
        QPushButton { background-color: #444; }
        QPushButton:hover { background-color: orange; }
        """
        buttons = (
            new_button,
            save_button,
            update_button,
            diff_button
        )
        for b in buttons:
            popup_bar.layout().addWidget(b)
            b.setStyleSheet(stylesheet)

        # wire signals into buttons
        new = partial(
            self.load_into_new_tab,
            subscript
        )
        new_button.clicked.connect(new)
        new_button.clicked.connect(remove)
        save = partial(
            self.save_this_version,
            subscript
        )
        save_button.clicked.connect(save)
        save_button.clicked.connect(remove)
        update = partial(
            self.update_from_autosave,
            subscript
        )
        update_button.clicked.connect(update)
        update_button.clicked.connect(remove)

        show_diff = partial(
            self.show_diff_text,
            subscript.text
        )
        diff_button.clicked.connect(show_diff)

        self.editor.modificationChanged.connect(
            self.check_diff_modified
        )

        # self.animate_popup()

    def animate_popup(self, start=0, end=46):
        """
        FIXME: This works in the prototype, but
        not here yet. Perhaps because it's called
        via a few signals, or something to do with
        the parent object being the tabeditor while
        the class is instantiated on the tabeditor's
        parent class, pythoneditor.
        """
        anim = QtCore.QPropertyAnimation(
            self.popup_bar,
            'maximumHeight'
        )
        self._anim = anim
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setDuration(400)
        anim.start()

    def remove_existing_popups(self, name=None):
        """
        Remove widgets with objectName
        "name" from the tabeditor layout.
        """
        layout = self.tabeditor.layout()
        # first remove any previous widgets
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item is None:
                continue
            widget = item.widget()
            if widget.objectName() != name:
                continue
            layout.removeItem(item)
            widget.deleteLater()

    def show_diff_text(self, text):
        editor_text = self.editor.toPlainText()
        l1 = text.splitlines(True)
        l2 = editor_text.splitlines(True)

        ctx_diff = difflib.context_diff(l1, l2)
        diff_text = ''
        for i in ctx_diff:
            diff_text += i

        self.diff_editor = editor.Editor()
        self.diff_editor.setPlainText(diff_text)
        self.diff_editor.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint
        )

        self.diff_editor.show()

    def load_into_new_tab(self, s):
        text = self.editor.toPlainText()
        self.editor.replace_text(s.text)
        self.tabs['text'] = s.text
        self.autosave()

        self.tabs.new_tab(
            tab_name=self.tabs['name'],
            tab_data={
            'text'  : text,
            'path'  : self.tabs['path'],
            }
        )
        self.autosave()

    def save_this_version(self, subscript):
        text = self.editor.toPlainText()
        subscript.text = text
        self.tabs['text'] = text
        self.autosave()

    def update_from_autosave(self, subscript):
        self.editor.replace_text(subscript.text)
        self.tabs['text'] = subscript.text
        self.autosave()

    def check_diff_modified(self):
        self.editor.modificationChanged.disconnect(
            self.check_diff_modified
        )
        self.check_autosave_modified()

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
        self.editor.document().setModified(False)
        self.sync_tab_indices()

    @QtCore.Slot(str, str, str, str, object)
    def save_by_uuid(self, uid, name, text, index, path=None):
        """ Only update a specific subscript given by uuid.
        """
        root, subscripts = parsexml('subscript')

        for s in subscripts:
            if s.attrib.get('uuid') == uid:
                sub = s
                break
        else:
            sub = ETree.Element('subscript')
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
        Store a <currentindex> element in order
        to restore the current index on readautosave.
        (if present, for backwards compatibility).
        """
        root, index_elements = parsexml('current_index')
        if len(index_elements) == 0:
            ci = ETree.Element('current_index')
            root.append(ci)
        else:
            ci = index_elements[0]
        ci.text = str(self.tabs.currentIndex())
        writexml(root)

    @QtCore.Slot(int, int)
    def update_tab_index(self, from_index, to_index):
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
        """ After saving the editor's contents,
        store the path to the saved file in the
        autosave attributes. The text contents
        are retained in the autosave until the
        file is closed, at which time a diff is
        attempted of the saved file and the
        autosave.

        :param uid: Unique Identifier of
                    subscript to save
        """
        # find the tab by uid
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
        if not is_file(path):
            return

        root, subscripts = parsexml('subscript')
        # we first look for an existing 
        # subscript that matches the uid
        for s in subscripts:
            if s.attrib.get('uuid') != uid:
                continue
            s.attrib['path'] = path
            break
        else:
            # if none is found we create 
            # a new subscript
            self.save_by_uuid(
                uid,
                self.tabs['name'],
                '', # don't save text unless document modified
                    # which it won't be on first open
                str(self.tabs.currentIndex()),
                path
            )
            data['saved'] = True
            self.tabs.setTabData(index, data)
            # FIXME: this doesn't save the 'saved' attrib of the tab at this point
            # and doesn't reload the document correctly. check the readautosave.
            return
        data['saved'] = True
        self.tabs.setTabData(index, data)
        writexml(root)

    @QtCore.Slot(object, int)
    def handle_tab_moved(self, editor, tab_index):
        self.autosave()

    @QtCore.Slot(int)
    def handle_tab_close(self, tab_index):
        """ Called on tabCloseRequested
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

        :param uid: Unique Identifier of
                    subscript to remove
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


def autosave_can_be_parsed():
    """ Return True if the autosave file
    is writable and not corrupted.
    """
    global AUTOSAVE_FILE
    xmlp = ETree.XMLParser(encoding="utf-8")
    try:
        parser = ETree.parse(AUTOSAVE_FILE, xmlp)
        return True
    except Exception:
        return False


# FIXME: redefined below. this is the deprecated version.
# test functionality is the same and delete this version.
def create_autosave_file():
    """ Create the autosave file into which
    PythonEditor stores all tab contents.
    """
    # look for the autosave
    if os.path.isfile(AUTOSAVE_FILE):

        # if the autosave file is empty, write header
        # FIXME: can this be an os.stat/get file size?
        # Furthermore, what if it's not empty but has a
        # corrupted header? What are the methods for
        # data preservation?
        with open(AUTOSAVE_FILE, 'r') as f:
            is_empty = not bool(f.read().strip())
        if is_empty:
            create_empty_autosave()
    else:

        # if file not found, check if directory exists
        if not os.path.isdir(NUKE_DIR):
            # filehandle, filepath = tempfile.mkstemp()
            # FIXME: set os.environ['PYTHONEDITOR_AUTOSAVE_FILE'] and define_autosave_path()
            # msg = 'Directory %s does not exist, saving to %s' % (NUKE_DIR, filepath)
            msg = 'Directory {0} does not exist'.format(NUKE_DIR)
            raise CouldNotCreateAutosave(msg)
        else:
            create_empty_autosave()
    return True


def create_autosave_file():
    """ Create the autosave file into which
    PythonEditor stores all tab contents.
    """
    global AUTOSAVE_FILE
    if autosave_can_be_parsed():
        return True
    if os.path.isfile(AUTOSAVE_FILE):
        fix_broken_xml()
        if autosave_can_be_parsed():
            return True
        raise CouldNotCreateAutosave()

    try:
        create_empty_autosave()
        return True
    except Exception as error:
        raise CouldNotCreateAutosave(error)


def create_empty_autosave():
    """ Write the default file header into the xml file.
    Overwrites any existing file.
    """
    with open(AUTOSAVE_FILE, 'w') as f:
        f.write(XML_HEADER+'<script></script>')


def get_editor_xml():
    if not create_autosave_file():
        return
    parser = ETree.parse(AUTOSAVE_FILE)
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

        element = ETree.Element('external_editor_path')
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
    """ Retrieve the root and a list of <element_name>
    elements from a given xml file.
    """
    if not create_autosave_file():
        return

    try:
        xmlp = ETree.XMLParser(encoding="utf-8")
        parser = ETree.parse(path, xmlp)
    except ETree.ParseError as e:
        print('ETree.ParseError', e)
        parser = fix_broken_xml(path)

    root = parser.getroot()
    elements = root.findall(element_name)
    return root, elements


TEMP_FILE = None
def writexml(root, path=AUTOSAVE_FILE):
    """ Attempt to write xml element
    to a file as a string. If the
    save fails, write to a temporary
    file instead.

    :param root: The xml element to write.
    :type  root: <type 'Element'>
    :param path: The path to save to.
    :type  path: <type 'str'>
    """
    data = ETree.tostring(root)
    data = data.decode('utf-8')

    # for neatness in the xml file.
    data = data.replace('><subscript', '>\n<subscript')
    data = data.replace('</subscript><', '</subscript>\n<')

    try:
        with io.open(
            path, 'wt', encoding='utf8', errors='ignore'
        ) as f:
            f.write(XML_HEADER+data)
    except IOError as e:
        msg = "Couldn't write to {0}\n".format(path)
        msg += "due to the following error:\n{0}".format(e)
        print(msg)

        global TEMP_FILE
        if (
            TEMP_FILE is None
            or not os.path.isfile(TEMP_FILE)
            ):
            fd, TEMP_FILE = tempfile.mkstemp()
            TEMP_FILE += '.xml'
        print('Writing to {0}'.format(TEMP_FILE))
        with io.open(
            TEMP_FILE, 'wt', encoding='utf8', errors='ignore'
        ) as f:
            f.write(XML_HEADER+data)


def fix_broken_xml(path=AUTOSAVE_FILE):
    """ Removes unwanted characters and
    (in case necessary in future
    implementations..) fixes other
    parsing errors with the xml file.
    """
    with io.open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    safe_string = remove_control_characters(content)

    with open(path, 'wt') as f:
        f.write(safe_string)

    xmlp = ETree.XMLParser(encoding="utf-8")
    try:
        parser = ETree.parse(path, xmlp)
    except ETree.ParseError:
        print('Fatal Error with xml structure. A backup of your autosave has been made.')
        backup_autosave_file(path, content)
        create_empty_autosave()
        xmlp = ETree.XMLParser(encoding="utf-8")
        parser = ETree.parse(path, xmlp)
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
        if s.text:
            continue
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
