from __future__ import print_function
from PythonEditor.ui.Qt import QtWidgets, QtCore, QtGui
from PythonEditor.ui import editor as EDITOR


class EditTabs(QtWidgets.QTabWidget):
    """
    QTabWidget containing Editor
    QPlainTextEdit widgets.
    """
    reset_tab_signal = QtCore.Signal()
    closed_tab_signal = QtCore.Signal(object)
    tab_switched_signal = QtCore.Signal(int, int, bool)
    contents_saved_signal = QtCore.Signal(object)
    tab_moved_signal = QtCore.Signal(object, int)

    def __init__(self):
        QtWidgets.QTabWidget.__init__(self)
        self.setTabBar(TabBar(self))

        self.setTabsClosable(True)
        self.user_cancelled_tab_close = False
        self.setTabShape(QtWidgets.QTabWidget.Rounded)

        self.tab_count = 0
        self.current_index = 0

        tabBar = self.tabBar()
        tabBar.setMovable(True)
        tabBar.tabMoved.connect(self.tab_restrict_move,
                                QtCore.Qt.DirectConnection)

        self.setup_new_tab_btn()
        self.tabCloseRequested.connect(self.close_tab)
        self.reset_tab_signal.connect(self.reset_tabs)
        self.currentChanged.connect(self.widget_changed)
        self.setStyleSheet("QTabBar::tab { height: 24px; }")

        # add tab list button
        self.corner_button = QtWidgets.QPushButton(':')
        self.corner_button.setFixedSize(24, 24)
        self.corner_button.setStyleSheet("border: 5px solid black")
        self.corner_button.clicked.connect(self.show_tab_menu)
        self.setCornerWidget(self.corner_button,
                             corner=QtCore.Qt.TopRightCorner)

    # currently not in use
    @property
    def editor(self):
        widget = self.currentWidget()
        if widget.objectName() != 'Editor':
            raise Exception('Current Widget is not an Editor')
        return widget

    # currently not in use
    @editor.setter
    def editor(self, widget):
        if widget.objectName() != 'Editor':
            raise Exception('Current Widget is not an Editor')
        self.setCurrentWidget(widget)

    def show_tab_menu(self):
        """
        Show a list of tabs and go to the tab clicked.
        """
        menu = QtWidgets.QMenu()
        from functools import partial
        for i in range(self.count()):
            tab_name = self.tabText(i)
            if not tab_name.strip():
                button = self.tabBar().tabButton(i, QtWidgets.QTabBar.LeftSide)
                if not isinstance(button, TabButton):
                    continue
                tab_name = button.text()
            action = partial(self.setCurrentIndex, i)
            menu.addAction(tab_name, action)
        menu.exec_(QtGui.QCursor().pos())

    @QtCore.Slot(int, int)
    def tab_restrict_move(self, from_index, to_index):
        """
        Prevents tabs from being moved beyond the +
        new tab button.
        """
        if from_index >= self.count()-1:
            self.tabBar().moveTab(to_index, from_index)
            return

        for index in from_index, to_index:
            widget = self.widget(index)
            widget.tab_index = index
            if hasattr(widget, 'name'):
                self.tab_moved_signal.emit(widget, index)

    def setup_new_tab_btn(self):
        """
        Adds a new tab [+] button to the right of the tabs.
        """
        widget = QtWidgets.QWidget()
        widget.setObjectName('Tab_Widget_New_Button')
        self.insertTab(0, widget, '')
        nb = self.new_btn = QtWidgets.QToolButton()
        nb.setMinimumSize(QtCore.QSize(50, 10))
        nb.setText('+')  # you could set an icon instead of text
        nb.setAutoRaise(True)
        nb.clicked.connect(self.new_tab)

        tabBar = self.tabBar()
        tabBar.setTabButton(0, QtWidgets.QTabBar.RightSide, nb)
        tabBar.setTabEnabled(0, False)

    @QtCore.Slot(str)
    def new_tab(self, tab_name=None, init_features=True):
        """
        Creates a new tab.
        """
        count = self.count()
        index = 0 if count == 0 else count - 1
        editor = EDITOR.Editor(handle_shortcuts=False, init_features=init_features)

        if (tab_name is None
                or not tab_name):
            tab_name = 'Tab {0}'.format(index)

        editor.name = tab_name
        editor.tab_index = index

        self.insertTab(index,
                       editor,
                       tab_name
                       )
        self.setCurrentIndex(index)

        # relay the contents saved signal
        editor.contents_saved_signal.connect(self.contents_saved_signal)

        self.tab_count = self.count()
        self.current_index = self.currentIndex()
        editor.setFocus()
        return editor

    def close_current_tab(self):
        """
        Closes the active tab. Called via shortcut key.
        """
        _index = self.currentIndex()
        self.tabCloseRequested.emit(_index)

    def close_tab(self, index):
        """
        Remove current tab if tab count is greater than 3 (so that the
        last tab left open is not the new button tab, although a better
        solution here is to open a new tab if the only tab left open is
        the 'new tab' tab). Also emits a close signal which is used by the
        autosave to determine if an editor's contents need saving.
        """
        if self.count() < 3:
            return
        _index = self.currentIndex()

        editor = self.widget(index)
        if editor.objectName() == 'Tab_Widget_New_Button':
            return

        self.closed_tab_signal.emit(editor)
        # the below attribute may be altered
        # by a slot connected with DirectConnection
        if self.user_cancelled_tab_close:
            return

        editor.deleteLater()

        tab_on_left = (index < _index)
        last_tab_before_end = (_index == self.count()-2)

        self.removeTab(index)
        if tab_on_left or last_tab_before_end:
            _index -= 1
        self.setCurrentIndex(_index)
        self.tab_count = self.count()

    def reset_tabs(self):
        for index in reversed(range(self.count())):
            widget = self.widget(index)
            if widget is None:
                continue
            if widget.objectName() == 'Editor':
                self.removeTab(index)
        self.new_tab()

    @QtCore.Slot(int)
    def widget_changed(self, index):
        """
        Emits tab_switched_signal with current widget.
        """
        tabremoved = self.count() < self.tab_count
        previous = self.current_index
        current = self.currentIndex()
        self.tab_switched_signal.emit(previous,
                                      current,
                                      tabremoved)
        self.current_index = self.currentIndex()
        self.tab_count = self.count()

    def addTab(self, *args):
        """
        Insurance override to point to insertTab.
        args may be:
        const QString &text
        const QIcon &icon, const QString &text

        TODO: Needs testing.
        """
        debug('Warning. addTab override feature needs testing.')
        if len(args) == 1:
            label, = args
            return self.insertTab(self.count(), None, label)
        elif len(args) == 2:
            icon, label = args
            return self.insertTab(self.count(), None, icon, label)
        else:
            return

        super(EditTabs, self).addTab(*args, **kwargs)

    def insertTab(self, *args):
        """
        Override overloaded method which can
        receive the following params:

        int index, QWidget widget, QString label
        int index, QWidget widget, QIcon icon, QString label
        """
        super(EditTabs, self).insertTab(*args)

        if len(args) == 3:
            index, widget, label = args
        elif len(args) == 4:
            index, widget, icon, label = args
        else:
            return

        if not isinstance(widget, EDITOR.Editor):
            return

        if not hasattr(self, 'tab_button_list'):
            # Note: button removed from set when tab removed.
            self.tab_button_list = set([])

        button = TabButton(label, widget)
        self.tab_button_list.add(button)
        self.setTabText(index, '')
        self.tabBar().setTabButton(index, QtWidgets.QTabBar.LeftSide, button)

    def removeTab(self, index):
        """
        Override QTabWidget method in order to also remove any buttons
        stored on the class. As this is the sole method for removing tabs
        uring a session, this should be sufficient to cleanup the
        list and prevent memory leaks.
        """
        button = self.tabBar().tabButton(index, QtWidgets.QTabBar.LeftSide)
        if button in self.tab_button_list:
            self.tab_button_list.remove(button)
        super(EditTabs, self).removeTab(index)

    def setTabText(self, index, label):
        """
        Override QTabWidget setTabText so that if the tab
        has a button, the text will be set on the button
        instead of the tab.
        """
        button = self.tabBar().tabButton(index, QtWidgets.QTabBar.LeftSide)
        if isinstance(button, TabButton):
            return button.setText(label)
        super(EditTabs, self).setTabText(index, label)


class TabBar(QtWidgets.QTabBar):
    def __init__(self, edittabs):
        super(TabBar, self).__init__()
        self.edittabs = edittabs

    def mouseDoubleClickEvent(self, event):
        """
        Initalise tab rename using lineedit
        on double left click.
        """
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.show_name_edit()
        super(TabBar, self).mouseDoubleClickEvent(event)

    def show_name_edit(self):
        """
        Shows a QLineEdit widget where the tab
        text is, allowing renaming of tabs.
        """
        self.rename_tab()

        editor = self.edittabs.currentWidget()
        if not editor.objectName() == 'Editor':
            return

        index = self.currentIndex()
        button = self.tabButton(index, QtWidgets.QTabBar.LeftSide)
        if isinstance(button, TabButton):
            label = button.text()
        else:
            label = self.tabText(index)

        self.editor = editor
        self.tab_text = label
        self.tab_index = index
        self.setTabText(index, '')

        self.name_edit = QtWidgets.QLineEdit(self)
        self.name_edit.editingFinished.connect(self.rename_tab)
        self.name_edit.setText(label)
        self.name_edit.selectAll()

        self.setTabButton(index,
                          QtWidgets.QTabBar.LeftSide,
                          self.name_edit)

        self.name_edit.setFocus(QtCore.Qt.MouseFocusReason)

    def rename_tab(self):
        """
        Sets the label of the current tab, then sets
        the editor 'name' property and refreshes the
        editor text to trigger the autosave which
        updates the name in the xml element.
        TODO: Needs to be the active tab to
        commit to the xml file!
        """
        if not (hasattr(self, 'name_edit')
                and self.name_edit.isVisible()):
            return

        self.name_edit.hide()

        text = self.name_edit.text().strip()
        if not bool(text):
            text = self.tab_text

        for tab_index in range(self.edittabs.count()):
            if self.edittabs.widget(tab_index) == self.editor:
                self.tab_index = tab_index

        button = self.tabButton(self.tab_index, QtWidgets.QTabBar.LeftSide)
        if isinstance(button, TabButton):
            button.setText(text)
        else:
            self.setTabText(self.tab_index, text)
            self.setTabButton(self.tab_index,
                              QtWidgets.QTabBar.LeftSide,
                              None)

        editor = self.editor
        self.edittabs.setCurrentIndex(self.tab_index)
        if editor.objectName() == 'Editor':
            editor.name = text
            read_only = editor.read_only
            editor.setPlainText(editor.toPlainText()) # force a refresh to update autosave with new name
            editor.read_only = read_only


class TabButton(QtWidgets.QLabel):
    """
    Labels for tabs that allow read-only
    state to be displayed as italics, or
    modified state as a small circle.
    """
    def __init__(self, text, editor):
        super(TabButton, self).__init__(text)
        self.editor = editor
        self.editor.read_only_signal.connect(self.set_read_state)
        self.editor.uid_signal.connect(self.uid_update)
        self.setStyleSheet('font: italic;')
        self._uid = None

    @QtCore.Slot(bool)
    def set_read_state(self, read_only):
        if read_only:
            self.setStyleSheet('font: italic;')
        else:
            self.setStyleSheet('')

    @QtCore.Slot(str)
    def uid_update(self, uid):
        """
        Note: Not yet using the uid for anything,
        If this doesn't become useful it's probably
        best removed.
        """
        self._uid = uid

