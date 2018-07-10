from __future__ import print_function
from PythonEditor.ui.Qt import QtWidgets, QtCore
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

    def __init__(self):
        QtWidgets.QTabWidget.__init__(self)
        self.setTabBar(TabBar(self))
        self.setTabsClosable(True)
        self.setTabShape(QtWidgets.QTabWidget.Rounded)

        self.tab_count = 0
        self.current_index = 0

        tabBar = self.tabBar()
        tabBar.setMovable(True)
        tabBar.tabMoved.connect(self.tab_restrict_move)

        self.setup_new_tab_btn()
        self.tabCloseRequested.connect(self.close_tab)
        self.reset_tab_signal.connect(self.reset_tabs)
        self.currentChanged.connect(self.widgetChanged)
        self.setStyleSheet("QTabBar::tab { height: 24px; }")

    @QtCore.Slot(int, int)
    def tab_restrict_move(self, from_index, to_index):
        """
        Prevents tabs from being moved beyond the +
        new tab button.
        """
        if from_index >= self.count()-1:
            self.tabBar().moveTab(to_index, from_index)

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
    def new_tab(self, tab_name=None):
        """
        Creates a new tab.
        """
        count = self.count()
        index = 0 if count == 0 else count - 1
        editor = EDITOR.Editor(handle_shortcuts=False)

        if (tab_name is None
                or not tab_name):
            tab_name = 'Tab {0}'.format(index)

        editor.name = tab_name

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
        Closes the active tab.
        """
        _index = self.currentIndex()
        self.tabCloseRequested.emit(_index)

    def close_tab(self, index):
        if self.count() < 3:
            return
        _index = self.currentIndex()

        editor = self.widget(index)
        if editor.objectName() == 'Tab_Widget_New_Button':
            return

        self.closed_tab_signal.emit(editor)
        editor.deleteLater()

        self.removeTab(index)
        index = self.count() - 1
        self.setCurrentIndex(_index-1)
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
    def widgetChanged(self, index):
        """
        Triggers widget_changed signal with current widget.
        TODO: Investigate why this sometimes seems to cause
        signal connection errors in autosavexml and shortcuts.
        """
        tabremoved = self.count() < self.tab_count
        previous = self.current_index
        current = self.currentIndex()
        self.tab_switched_signal.emit(previous,
                                      current,
                                      tabremoved)
        self.current_index = self.currentIndex()
        self.tab_count = self.count()


class TabBar(QtWidgets.QTabBar):
    def __init__(self, edittabs):
        super(TabBar, self).__init__()
        self.edittabs = edittabs

    def mouseDoubleClickEvent(self, event):
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
        title = self.tabText(index)

        self.editor = editor
        self.tab_text = title
        self.tab_index = index
        self.setTabText(index, '')

        self.name_edit = QtWidgets.QLineEdit(self)
        self.name_edit.editingFinished.connect(self.rename_tab)
        self.name_edit.setText(title)
        self.name_edit.selectAll()

        self.setTabButton(index,
                          QtWidgets.QTabBar.LeftSide,
                          self.name_edit)

        self.name_edit.setFocus(QtCore.Qt.MouseFocusReason)

    def rename_tab(self):
        """
        Sets the title of the current tab, then sets
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

        self.setTabText(self.tab_index, text)
        self.setTabButton(self.tab_index,
                          QtWidgets.QTabBar.LeftSide,
                          None)

        editor = self.editor
        self.edittabs.setCurrentIndex(self.tab_index)
        if editor.objectName() == 'Editor':
            editor.name = text
            editor.setPlainText(editor.toPlainText())
