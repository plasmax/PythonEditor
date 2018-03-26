from Qt import QtWidgets, QtCore
from editor import Editor

class EditTabs(QtWidgets.QTabWidget):
    """
    QTabWidget containing Editor
    QPlainTextEdit widgets.
    """
    widget_changed_signal = QtCore.Signal(object)

    def __init__(self):
        QtWidgets.QTabWidget.__init__(self)
        self.setTabsClosable(True)
        self.new_tab()
        self._build_tabs()
        self.currentChanged.connect(self.widgetChanged)
        self.tabCloseRequested.connect(self.closeTab)

    def _build_tabs(self):
        self.insertTab(1, QtWidgets.QWidget(),'')
        nb = self.new_btn = QtWidgets.QToolButton()
        nb.setMinimumSize(QtCore.QSize(50,10))
        nb.setText('+') # you could set an icon instead of text
        nb.setAutoRaise(True)
        nb.clicked.connect(self.new_tab)
        self.tabBar().setTabButton(1, QtWidgets.QTabBar.RightSide, nb)
        self.tabBar().setTabEnabled(1, False)

    @QtCore.Slot(str)
    def new_tab(self):
        index = self.count() - 1
        editor = Editor()
        self.insertTab(index, 
                       editor, 
                       'New Tab')
        self.setCurrentIndex(index)

    def closeTab(self, index):
        _index = self.currentIndex()
        self.removeTab(index)
        index = self.count() - 1
        self.setCurrentIndex(_index-1)

    @QtCore.Slot(int)
    def widgetChanged(self, index):
        """
        Triggers widget_changed signal
        with current widget.
        """
        self.widget_changed_signal.emit(self.currentWidget())
