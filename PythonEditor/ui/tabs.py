"""
A nice solution using a single editor and
a subclassed QTabBar with

need my new tab button!!!! and menu

update the tab dict['text'] on every keypress
then pick it up smoothly with a background thread
reading the dict data
"""

import time
import os
from Qt import QtWidgets, QtGui, QtCore
from PythonEditor.ui.features import autosavexml
from PythonEditor.ui import editor


# # class Tab(dict):
# class Tab(object):
#     uid = None
#     name = None
#     text = ''
#     path = ''
#     date = ''
#     def __setitem__(self, name, value):
#         setattr(self, name, value)
#         super(Tab, self).__setitem__(name, value)

#     def __getitem__(self, name):
#         print 'this is a tab'
#         return getattr(self, name)

#     def __repr__(self):
#         s = '<Tab {0}>'.format(self.name)
#         return s

#     # def update(self, key, value):
#     #     print key, value
#     #     super(Tab, self).update(key, value)


"""
tab = Tab()
for key, value in data.items():
    tab[key] = value
pprint(tab.__dict__)
"""


TAB_STYLESHEET = """
QTabBar::tab {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
    height: 24px;
    padding-right: 50px;
}
"""
TAB_STYLESHEET = """
QTabBar::tab {
    height: 24px;
    //border-top-right-radius: -15px;
}
/*
QTabBar::tab:selected {
    padding-right: 14px;
}
*/
"""


class Tabs(QtWidgets.QTabBar):
    """
    Make tabs fast by overriding the
    paintEvent to draw close buttons.

    Tabs are also more useful, storing more data
    which can be easily reached through this class.
    """
    pen = QtGui.QPen()
    brush = QtGui.QBrush()
    mouse_over_rect = False
    over_button = -1

    def __init__(self, *args):
        super(Tabs, self).__init__(*args)
        self.setStyleSheet(TAB_STYLESHEET)
        self.setMovable(True)

        self.setup_new_tab_btn()

    def setup_new_tab_btn(self):
        """
        Adds a new tab [+] button to the right of the tabs.
        """
        self.insertTab(0, '')
        nb = self.new_btn = QtWidgets.QToolButton()
        # nb.setMinimumSize(QtCore.QSize(50, 10))
        nb.setMaximumSize(QtCore.QSize(50, 10))
        nb.setText('+')  # you could set an icon instead of text
        nb.setAutoRaise(True)
        nb.clicked.connect(self.new_tab)

        data = {'new_tab': True}
        self.setTabData(0, data)
        self.setTabButton(0, QtWidgets.QTabBar.RightSide, nb)
        self.setTabEnabled(0, False)

    @QtCore.Slot(str)
    def new_tab(self, tab_name=None):
        """
        Creates a new tab.
        """
        count = self.count()
        index = 0 if count == 0 else count - 1

        if (tab_name is None
                or not tab_name):
            tab_name = 'Tab {0}     '.format(index)

        self.insertTab(index, tab_name)
        data = {
            'uuid' : None,
            'name' : tab_name,
            'text' : '',
            'path' : '',
            'date' : '',
        }

        self.setTabData(index, data)
        self.setCurrentIndex(index)

        # # relay the contents saved signal
        # editor.contents_saved_signal.connect(self.contents_saved_signal)

    def tab(self, index):
        return self.tabData(index)

    def __getitem__(self, name):
        """
        Allow easy lookup for
        the current tab's data.
        """
        index = self.currentIndex()
        return self.tabData(index)[name]

    def get(self, name):
        try:
            return self[name]
        except KeyError:
            return None

    def __setitem__(self, name, value):
        """
        Easily set current tab's value.
        """
        index = self.currentIndex()
        tab_data = self.tabData(index)
        tab_data[name] = value
        return self.setTabData(index, tab_data)

    def tab_close_button_rect(self, i):
        """
        Return a rectangle for the tab close
        button.
        """
        tab_rect = self.tabRect(i)
        button_rect = QtCore.QRect(tab_rect)
        w = tab_rect.right()-tab_rect.left()
        o = 5
        button_rect.adjust(w-25+o, 5, -15+o, -5)
        # could force it to be always square here...
        return button_rect

    def event(self, e):
        """
        Trigger button highlighting if
        hovering over (x) close buttons
        """
        if e.type() == QtCore.QEvent.Type.HoverMove:
            pt = e.pos()
            i = self.tabAt(pt)
            rect = self.tabRect(i)

            # if not self.rect().contains(rect):
                # continue # would be nice to optimise

            if rect.contains(pt):
                rqt = self.tab_close_button_rect(i)
                if rqt.contains(pt):
                    self.mouse_over_rect = True
                    self.over_button = i
                    self.repaint()
                else:
                    self.mouse_over_rect = False
                    self.over_button = -1
                    self.repaint()

            # for i in range(self.count()):
            #     rect = self.tabRect(i)

            #     if not self.rect().contains(rect):
            #         continue # would be nice to optimise

            #     if rect.contains(pt):
            #         rqt = self.tab_close_button_rect(i)
            #         if rqt.contains(pt):
            #             self.mouse_over_rect = True
            #             self.over_button = i
            #             self.repaint()
            #         else:
            #             self.mouse_over_rect = False
            #             self.over_button = -1
            #             self.repaint()
        return super(Tabs, self).event(e)

    def paint_close_button(self):
        """
        Let's draw a tiny little x on the right
        that's our new close button. It's just two little lines! x

        Notes:
        - it's probably faster if we only iterate over visible tabs.
        - How can this be used to write italic text?
        - we could change the x to a o like sublime
        """
        for i in range(self.count()-1):
            rect = self.tabRect(i)

            rqt = self.tab_close_button_rect(i)
            if not self.rect().contains(rqt):
                # would be nice to optimise by setting
                # a visible start-end at which to break
                #        v        v
                # -------[-------]-------
                continue

            x,y,r,t = rect.getCoords()

            p = QtGui.QPainter()
            p.begin(self)
            p.setBrush(self.brush)
            mouse_over = False
            if i == self.over_button:
                if self.mouse_over_rect:
                    mouse_over = True
                    brush = QtGui.QBrush(QtCore.Qt.gray)
                    p.setBrush(brush)
            p.setPen(None)
            p.setRenderHint(QtGui.QPainter.Antialiasing)

            p.setPen(self.pen)
            self.pen.setWidth(2)
            if i == self.over_button:
                if self.mouse_over_rect:
                    pen = QtGui.QPen(QtCore.Qt.white)
                    pen.setWidth(2)
                    p.setPen(pen)

            a = 3
            # rqt.adjust(a,a,-a,-a)
            rqt.adjust(0,3,0,-3)

            # make the shape square:
            w = rqt.width()
            h = rqt.height()
            if w > h:
                rqt.adjust(0,0, -abs(w-h), 0)
            elif h > w:
                rqt.adjust(0,0, 0, -abs(w-h))

            saved = self.tabData(i).get('state') != 'not_saved'
            if not saved and not mouse_over:
                p.drawEllipse(rqt)
            else:
                p.drawLine(rqt.bottomLeft(), rqt.topRight())
                p.drawLine(rqt.topLeft(), rqt.bottomRight())
            p.end()

    def paintEvent(self, e):
        super(Tabs, self).paintEvent(e)
        self.paint_close_button()

    def mousePressEvent(self, e):
        """
        If clicking on close buttons
        """
        if e.button() == QtCore.Qt.LeftButton:
            pt = e.pos()
            i = self.tabAt(pt)

            # handle name edit still being visible
            if hasattr(self, 'name_edit'):
                try:
                    if self.name_edit.isVisible():
                        if self.name_edit.tab_index != i:
                            self.rename_tab()
                except RuntimeError: # likely that the lineedit has been deleted
                    del self.name_edit

            # handle clicking on close button
            for i in range(self.count()):
                rect = self.tabRect(i)

                if rect.contains(pt):
                    rqt = self.tab_close_button_rect(i)
                    if rqt.contains(pt):
                        print 'clicked close on tab %s %s' % (i, self.tabText(i))
                        self.safe_remove_tab(i)
                        # if i >= self.count():
                        #     print 'this should '
                        #     self.setCurrentIndex(i-2)
                        return

        # if not returned, handle clicking on tab
        return super(Tabs, self).mousePressEvent(e)

    def mouseDoubleClickEvent(self, e):
        if e.button() == QtCore.Qt.LeftButton:
            self.show_name_edit()
        return super(Tabs, self).mouseDoubleClickEvent(e)

    def show_name_edit(self):
        """
        Shows a QLineEdit widget where the tab
        text is, allowing renaming of tabs.
        """
        try:
            self.rename_tab()
        except RuntimeError: # likely that the lineedit has been deleted
            del self.name_edit
            return

        index = self.currentIndex()
        button = self.tabButton(index, QtWidgets.QTabBar.LeftSide)
        label = self.tabText(index)

        self.tab_text = label
        self.tab_index = index
        self.setTabText(index, '')

        self.name_edit = QtWidgets.QLineEdit(self)
        rect = self.tabRect(index)
        self.name_edit.resize(self.name_edit.width(), rect.height()-7)
        self.name_edit.tab_index = index
        self.name_edit.editingFinished.connect(self.rename_tab)
        self.name_edit.setText(label.strip())
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

        self.tab_index = self.currentIndex()

        button = self.tabButton(self.tab_index, QtWidgets.QTabBar.LeftSide)

        self.setTabText(self.tab_index, text+' '*5)
        self.setTabButton(self.tab_index,
                          QtWidgets.QTabBar.LeftSide,
                          None)

    def safe_remove_tab(self, index):
        """
        Remove current tab if tab count is greater than 3 (so that the
        last tab left open is not the new button tab, although a better
        solution here is to open a new tab if the only tab left open is
        the 'new tab' tab). Also emits a close signal which is used by the
        autosave to determine if an editor's contents need saving.
        """
        if self.tabData(index).get('state') == 'not_saved':
            raise NotImplementedError('ask if tab should be saved')
            return

        if self.count() < 3:
            return
        _index = self.currentIndex()

        if self.tabData(index).get('new_tab') == True:
            return # it's the [+] new tab button

        """
        # safeguard - this is where the user is asked if they want to save
        # TODO: could be done via tab state instead, or put the dialog in here
        self.closed_tab_signal.emit(editor)
        # the below attribute may be altered
        # by a slot connected with DirectConnection
        if self.user_cancelled_tab_close:
            return
        """

        tab_on_left = (index < _index)
        last_tab_before_end = (_index == self.count()-2)

        self.removeTab(index) # this should emit a close signal like the current tabwidget
        if tab_on_left or last_tab_before_end:
            _index -= 1
        self.setCurrentIndex(_index)
        self.tab_count = self.count()


class TabContainer(QtWidgets.QWidget):
    """
    Replacement QTabWidget
    Contains a QTabBar and a single Editor.
    """
    # for autosave purposes:
    reset_tab_signal = QtCore.Signal()
    closed_tab_signal = QtCore.Signal(object) # in case we receive a ctrl+shift+w signal to close the tab
    tab_switched_signal = QtCore.Signal(int, int, bool)
    contents_saved_signal = QtCore.Signal(object)
    tab_moved_signal = QtCore.Signal(object, int)

    def __init__(self):
        super(TabContainer, self).__init__()
        self._layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self._layout)

        self.tab_widget = QtWidgets.QWidget()
        self.tab_widget_layout = QtWidgets.QHBoxLayout(self.tab_widget)
        self.tab_widget_layout.setContentsMargins(0,0,0,0)
        self.tabs = Tabs()
        self.tab_widget_layout.addWidget(self.tabs)
        # add tab list button
        self.corner_button = QtWidgets.QPushButton(':')
        self.corner_button.setFixedSize(24, 24)
        self.corner_button.setStyleSheet("border: 5px solid black")
        self.tab_widget_layout.addWidget(self.corner_button)

        self.editor = editor.Editor(handle_shortcuts=False)

        for widget in self.tab_widget, self.editor:
            self.layout().addWidget(widget)

    def post_init_load_contents(self):
        """
        Separate connecting Signals until after all tab data
        is loaded in order to speed up initial loading.
        Also setup editor with first tab text contents.
        """
        self.tabs.setCurrentIndex(self.tabs.count())
        current_index = self.tabs.currentIndex()
        self.set_editor_contents(current_index)
        self.connect_signals()

    def connect_signals(self):
        """
        We probably want to run this after tabs are loaded.
        """
        self.tabs.currentChanged.connect(self.set_editor_contents)

        # this is something we're going to want only
        # when tab already set (and not when switching)
        # self.editor.modificationChanged.connect(self.save_text_in_tab)
        # self.editor.textChanged.connect(self.save_text_in_tab)
        self.editor.post_key_pressed_signal.connect(self.save_text_in_tab)
        self.tabs.tabMoved.connect(self.tab_restrict_move,
                                QtCore.Qt.DirectConnection)
        self.corner_button.clicked.connect(self.show_tab_menu)

    def show_tab_menu(self):
        """
        Show a list of tabs and go to the tab clicked.
        """
        menu = QtWidgets.QMenu()
        from functools import partial
        for i in range(self.tabs.count()):
            tab_name = self.tabs.tabText(i)
            if not tab_name.strip():
                continue
                # button = self.tabs.tabButton(i, QtWidgets.QTabBar.LeftSide)
                # if not isinstance(button, TabButton):
                #     continue
                # tab_name = button.text()
            action = partial(self.tabs.setCurrentIndex, i)
            menu.addAction(tab_name, action)
        menu.exec_(QtGui.QCursor().pos())

    def new_tab(self):
        pass

    def close_current_tab(self):
        pass

    @QtCore.Slot(int)
    def set_editor_contents(self, index):
        """
        Set editor contents to the data
        found in tab #index
        """
        data = self.tabs.tabData(index)
        text = data['text']

        if text is None or not text.strip():
            path = data.get('path')
            if path is None:
                text = ''
                # raise Exception('editor with no text and no path!')
            elif not os.path.isfile(path):
                text = ''
                # raise Exception('editor with no text and invalid path!')
            else:
                with open(path, 'r') as f:
                    text = f.read()
                data['text'] = text

        self.editor.setPlainText(text)
        self.editor.name = data['name']
        self.editor.uid = data['uuid']
        self.editor.path = data.get('path')

    def save_text_in_tab(self):
        """
        Store the editor's current text
        in the current tab
        """
        print 'changed, saving text in tab. we want this to be the user entering text only!'

        if self.editor.uid == self.tabs['uuid']:
            self.tabs['text'] = self.editor.toPlainText()
            if self.tabs.get('state') != 'not_saved':
                self.tabs['state'] = 'not_saved'
                self.tabs.repaint()

    @QtCore.Slot(int, int)
    def tab_restrict_move(self, from_index, to_index):
        """
        Prevents tabs from being moved beyond the +
        new tab button.
        """
        if from_index >= self.count()-1:
            self.tabs.moveTab(to_index, from_index)
            return

        # do this by uid
        # for index in from_index, to_index:
        #     widget = self.widget(index)
        #     widget.tab_index = index
        #     if hasattr(widget, 'name'):
        #         self.tab_moved_signal.emit(widget, index)


"""
def check_changed():
    # Check in with our little tab to see if anything's new.
    root, subscripts = autosavexml.parsexml('subscript')
    for s in subscripts:
        if s.attrib.get('uuid') == tabs['uuid']:
            if tabs['text'] != s.text:
                print 'updated text!'
                # this is where we'll actually write
                # the text to the autosave

timer = QtCore.QTimer()
timer.timeout.connect(check_changed)
timer.setInterval(200)
timer.start()
timer.stop()
"""


if __name__ == '__main__':
    #testing!
    tc = TabContainer()




    # # -------------------- AUTOSAVEXML ------------------ #
    # # loading the autosave
    # root, subscripts = autosavexml.parsexml('subscript')

    # autosaves = []
    # i = 0
    # for s in subscripts:
    #     name = s.attrib.get('name')
    #     if name is None:
    #         continue
    #     autosaves.append((i, s))
    #     i += 1

    # # storing autosave into new tabs
    # for i, s in autosaves:
    #     name = s.attrib.get('name')
    #     data = s.attrib.copy()
    #     tc.tabs.addTab(name+' '*5) # hax for enough space for close button :'(
    #     path = data.get('path')
    #     if path is not None:
    #         tc.tabs.setTabToolTip(i, path) # and if this changes?
    #     data['text'] = s.text # we might need to fetch the text from a file
    #     tc.tabs.setTabData(i, data)

    # # set the tc.tabs to the last loaded
    # tc.tabs.setCurrentIndex(i)
