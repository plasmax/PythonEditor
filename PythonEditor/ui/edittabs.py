from Qt import QtWidgets, QtCore
from PythonEditor.ui import editor as EDITOR

class EditTabs(QtWidgets.QTabWidget):
    """
    QTabWidget containing Editor
    QPlainTextEdit widgets.
    TODO: Set stylesheet to 
    have tabs the same height as Nuke's.
    """
    tab_switched_signal = QtCore.Signal(int, int, bool)

    def __init__(self):
        QtWidgets.QTabWidget.__init__(self)
        self.setTabsClosable(True)
        self.setTabShape(QtWidgets.QTabWidget.Rounded)

        self.tab_count = 0
        self.current_index = 0

        tabBar = self.tabBar()
        tabBar.setMovable(True)
        tabBar.tabMoved.connect(self.tab_restrict_move)

        self.setup_new_tab_btn()
        self.current_editor = None
        self.tabCloseRequested.connect(self.close_tab)
        self.currentChanged.connect(self.widgetChanged)
        self.setStyleSheet("QTabBar::tab { height: 25px; }")

    @QtCore.Slot(int, int)
    def tab_restrict_move(self, from_index, to_index):
        """
        Prevents tabs from being moved beyond the +
        new tab button.
        """
        if from_index >= self.count()-1:
            self.tabBar().moveTab(to_index, from_index)

    def setup_new_tab_btn(self):
        self.insertTab(0, QtWidgets.QWidget(),'')
        nb = self.new_btn = QtWidgets.QToolButton()
        nb.setObjectName('Tab_Widget_New_Button')
        nb.setMinimumSize(QtCore.QSize(50,10))
        nb.setText('+') # you could set an icon instead of text
        nb.setAutoRaise(True)
        nb.clicked.connect(self.new_tab)

        tabBar = self.tabBar()
        tabBar.setTabButton(0, QtWidgets.QTabBar.RightSide, nb)
        tabBar.setTabEnabled(0, False)

    @QtCore.Slot(str)
    def new_tab(self):
        count = self.count()
        index = 0 if count == 0 else count - 1
        editor = EDITOR.Editor(handle_shortcuts=False)
        self.insertTab(index, 
                       editor, 
                       'Tab {0}'.format(index)
                       )
        self.setCurrentIndex(index)

        self.tab_count = self.count()
        self.current_index = self.currentIndex()
        editor.setFocus()
        return editor

    def close_current_tab(self):
        """
        TODO: 
        2) Maybe check to see if file contents is saved 
        somewhere. 
        """
        _index = self.currentIndex()
        self.close_tab(_index)

    def close_tab(self, index):
        if self.count() < 3:
            return
        _index = self.currentIndex()

        old_widget = self.widget(index)
        if old_widget.objectName() != 'Editor':
            return

        old_widget.deleteLater()

        self.removeTab(index)
        index = self.count() - 1
        self.setCurrentIndex(_index-1)
        self.tab_count = self.count()

    @QtCore.Slot(int)
    def widgetChanged(self, index):
        """
        Triggers widget_changed signal
        with current widget.
        """
        tabremoved = self.count() < self.tab_count
        previous = self.current_index
        current = self.currentIndex()
        self.tab_switched_signal.emit(previous, current, tabremoved)
        self.current_index = self.currentIndex()
        self.tab_count = self.count()