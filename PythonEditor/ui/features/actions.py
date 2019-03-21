from __future__ import print_function
import os
import uuid
import __main__
import inspect
import subprocess
from PythonEditor.ui.Qt import QtWidgets, QtGui, QtCore
from PythonEditor.utils import save


REGISTER = {
'editor': {
    'Print Help'            : 'print_help',
    'Open Module File'      : 'open_module_file',
    'Open Module Directory' : 'open_module_directory',
    'Search'                : 'search_input',
    },
'tabs': {
    },
'terminal': {
    },
}

class Actions(QtCore.QObject):
    """
    Collection of QActions that are
    accessible for menu and shortcut registry.
    """
    clear_output_signal = QtCore.Signal()
    exec_text_signal = QtCore.Signal()

    actions = {}
    def __init__(
            self,
            editor=None,
            tabeditor=None,
            terminal=None,
            use_tabs=True
        ):
        """
        :param use_tabs:
        If False, the parent_widget is the QPlainTextEdit (Editor)
        widget. If True, apply actions to the QTabBar as well as
        the Editor.
        """
        super(Actions, self).__init__()
        self.setObjectName('Actions')

        if editor is None:
            raise Exception('A text editor is necessary for this class.')
        self.editor = editor

        if tabeditor is not None:
            self.tabeditor = tabeditor
            self.tabs = tabeditor.tabs
            parent_widget = tabeditor
        else:
            parent_widget = editor

        if terminal is not None:
            self.terminal = terminal
            self.clear_output_signal.connect(self.terminal.clear)

        self.setParent(parent_widget)
        self.use_tabs = use_tabs

        self.create_action_register()

    def create_action_register(self):
        global REGISTER
        for widget_name, actions in REGISTER.items():
            widget = getattr(self, widget_name)
            if widget is None:
                continue
            for name, method in actions.items():
                if not isinstance(method, str):
                    continue
                func = getattr(self, method)
                action = make_action(name, widget, func)

    def print_help(self):
        """
        Prints documentation for selected text if
        it currently represents a python object.
        """
        cursor = self.editor.textCursor()
        selection = cursor.selection()
        text = selection.toPlainText().strip()
        if not text:
            return
        obj = __main__.__dict__.get(text)
        if obj is not None:
            print(obj.__doc__)
        elif text:
            exec('help('+text+')', __main__.__dict__)

    def open_module_file(self):
        textCursor = self.editor.textCursor()
        text = textCursor.selection().toPlainText()
        if not text.strip():
            return

        obj = get_subobject(text)
        open_module_file(obj)

    def open_module_directory(self):
        textCursor = self.editor.textCursor()
        text = textCursor.selection().toPlainText()
        if not text.strip():
            return

        obj = get_subobject(text)
        open_module_directory(obj)

    def search_input(self):
        """
        Very basic search dialog.
        """
        getText = QtWidgets.QInputDialog.getText
        dialog = getText(self.editor, 'Search', '',)
        text, ok = dialog
        if not ok:
            return

        textCursor = self.editor.textCursor()
        original_pos = textCursor.position()

        # start the search from the beginning of the document
        textCursor.setPosition(0, QtGui.QTextCursor.MoveAnchor)
        document = self.editor.document()
        cursor = document.find(text, textCursor)
        pos = cursor.position()
        if pos != -1:
            self.editor.setTextCursor(cursor)


def make_action(name, widget, func):
    """
    Add action to widget with
    given triggered function.

    :action: QtWidgets.QAction
    :widget: QtWidgets.QWidget
    :func: a callable that gets executed
           when triggering the action.
    """
    action = QtWidgets.QAction(widget)
    action.triggered.connect(func)
    widget.addAction(action)
    action.setText(name)
    return action


def toggle_backslashes_in_string(text):
    if '\\' in text:
        text = text.replace('\\\\', '/')
        text = text.replace('\\', '/')
    elif '/' in text:
        text = text.replace('/', '\\')
    return text


def toggle_backslashes(editor):
    textCursor = editor.textCursor()
    selection = textCursor.selection()
    text = selection.toPlainText()
    if not text:
        textCursor.select(QtGui.QTextCursor.BlockUnderCursor)
        text = textCursor.selectedText()

    edited_text = toggle_backslashes_in_string(text)
    if edited_text == text:
        return
    textCursor.insertText(text)


def save_action(tabs, editor):
    """
    """
    path = tabs.get('path')
    text = editor.toPlainText()
    path = save.save(text, path)
    if path is None:
        return
    tabs['path'] = path
    tabs['saved'] = True
    # notify the autosave to empty entry
    tabs.contents_saved_signal.emit(tabs['uuid'])


def open_action(tabs, editor):
    """
    Simple open file.
    :tabs: TabBar
    :editor: Editor
    """
    o = QtWidgets.QFileDialog.getOpenFileName
    path, _ = o(tabs, "Open File")
    if not path:
        return

    with open(path, 'rt') as f:
        text = f.read()

    for index in range(tabs.count()):
        data = tabs.tabData(index)
        if data is None:
            continue

        if data.get('path') != path:
            continue

        # try to avoid more costly 2nd comparison
        if data.get('text') == text:
            tabs.setCurrentIndex(index)
            return

    tab_name = os.path.basename(path)

    # Because the document will be open in read-only mode, the
    # autosave should not save the editor's contents until the
    # contents have been modified.
    data = {
        'uuid'  : str(uuid.uuid4()),
        'name'  : tab_name,
        'text'  : '',
        'path'  : path,
        'date'  : '', # need the file's date
        'saved' : True, # read-only
    }

    tabs.new_tab(tab_name=tab_name)
    editor.setPlainText(text)


def get_subobject(text):
    """
    Walk down an object's hierarchy to retrieve
    the object at the end of the chain.
    """
    text = text.strip()
    if '.' not in text:
        return __main__.__dict__.get(text)

    name = text.split('.')[0]
    obj = __main__.__dict__.get(name)
    if obj is None:
        return

    for name in text.split('.')[1:]:
        obj = getattr(obj, name)
        if obj is None:
            return
    return obj


def open_module_file(obj):
    try:
        file = inspect.getfile(obj)
    except TypeError as e:
        if hasattr(obj, '__class__'):
            obj = obj.__class__
            try:
                file = inspect.getfile(obj)
            except TypeError as e:
                print(e)
                return
        else:
            print(e)
            return

    if file.endswith('.pyc'):
        file = file.replace('.pyc', '.py')

    try:
        lines, lineno = inspect.getsourcelines(obj)
        file = file+':'+str(lineno)
    except AttributeError, IOError:
        pass

    print(file)

    #TODO: this is a horrible hack to avoid circular imports
    from PythonEditor.ui.features.autosavexml import get_external_editor_path

    EXTERNAL_EDITOR_PATH = get_external_editor_path()
    if (EXTERNAL_EDITOR_PATH
            and os.path.isdir(os.path.dirname(EXTERNAL_EDITOR_PATH))):
        subprocess.Popen([EXTERNAL_EDITOR_PATH, file])


def open_module_directory(obj):
    file = inspect.getfile(obj).replace('.pyc', '.py')
    folder = os.path.dirname(file)
    print(folder)

    #TODO: this is a horrible hack to avoid circular imports
    from PythonEditor.ui.features.autosavexml import get_external_editor_path

    EXTERNAL_EDITOR_PATH = get_external_editor_path()
    if (EXTERNAL_EDITOR_PATH
            and os.path.isdir(os.path.dirname(EXTERNAL_EDITOR_PATH))):
        subprocess.Popen([EXTERNAL_EDITOR_PATH, folder])


def openDir(module):
    try:
        print(bytes(module.__file__))
        subprocess.Popen(['nautilus', module.__file__])
    except AttributeError:
        file = inspect.getfile(module)
        subprocess.Popen(['nautilus', file])
    print('sublime ', __file__, ':', sys._getframe().f_lineno, sep='')  # TODO: nautilus is not multiplatform!
