"""
A nicer solution using a single editor and
a subclassed QTabBar.

TODO:
 x update the tab dict['text'] on every keypress
 - pick the dict data up with a background thread
"""

import time
import os
from Qt import QtWidgets, QtGui, QtCore
from PythonEditor.ui.features import autosavexml
from PythonEditor.ui import editor


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
        self.tab_pressed = False
        self.setStyleSheet(TAB_STYLESHEET)
        self.setMovable(True)

        self.setup_new_tab_btn()

    def setup_new_tab_btn(self):
        """
        Adds a new tab [+] button to the right of the tabs.
        """
        self.insertTab(0, '')
        nb = self.new_btn = QtWidgets.QToolButton()
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

    def tab_close_button_rect(self, tab_rect):
        """
        Return a rectangle for the tab close
        button.
        """
        # tab_rect = self.tabRect(i)
        button_rect = QtCore.QRect(tab_rect)
        w = tab_rect.right()-tab_rect.left()
        o = 5
        button_rect.adjust(w-25+o, 5, -15+o, -5)
        # could force it to be always square here...
        return button_rect

    def event(self, event):
        """
        Trigger button highlighting if
        hovering over (x) close buttons
        """
        if event.type() == QtCore.QEvent.Type.HoverMove:
            pt = event.pos()
            i = self.tabAt(pt)
            rect = self.tabRect(i)

            if rect.contains(pt):
                rqt = self.tab_close_button_rect(rect)
                if rqt.contains(pt):
                    self.mouse_over_rect = True
                    self.over_button = i
                    self.repaint()
                else:
                    self.mouse_over_rect = False
                    self.over_button = -1
                    self.repaint()

        return super(Tabs, self).event(event)

    def paint_close_button(self):
        """
        Let's draw a tiny little x on the right
        that's our new close button. It's just two little lines! x

        Notes:
        - it's probably faster if we only iterate over visible tabs.
        - How can this be used to write italic text?


        # paint a real close button!
        from Qt import QtCore, QtGui, QtWidgets

        tc = QtWidgets.QStyle.PE_IndicatorTabClose
        class W(QtWidgets.QWidget):
            def paintEvent(self, event):
                opt = QtWidgets.QStyleOption()
                opt.initFrom(self)
                p = QtGui.QPainter(self)
                s = self.style()
                s.drawPrimitive(tc, opt, p, self)

        w = W()
        w.show()

        from qtabbar.cpp:

        def CloseButton::paintEvent(QPaintEvent *)

            QPainter p(this);
            QStyleOption opt;
            opt.init(this);
            opt.state |= QStyle::State_AutoRaise;
            if (isEnabled() && underMouse() && !isChecked() && !isDown())
                opt.state |= QStyle::State_Raised;
            if (isChecked())
                opt.state |= QStyle::State_On;
            if (isDown())
                opt.state |= QStyle::State_Sunken;

            if (const QTabBar *tb = qobject_cast<const QTabBar *>(parent()))
                int index = tb->currentIndex();
                QTabBar::ButtonPosition position = (QTabBar::ButtonPosition)style()->styleHint(QStyle::SH_TabBar_CloseButtonPosition, 0, tb);
                if (tb->tabButton(index, position) == this)
                    opt.state |= QStyle::State_Selected;


            style()->drawPrimitive(QStyle::PE_IndicatorTabClose, &opt, &p, this);

        """
        for i in range(self.count()-1):
            rect = self.tabRect(i)

            """
            # TODO: make buttons follow the tabs properly
            # when moving. This should also take into account
            # the tab that moves underneath
            if self.tab_pressed and i == self.pressedIndex:
                data = self.tabData(i)
                if data.get('dragDistance') is not None:
                    dist = data['dragDistance']
                    mv = rect.x()+dist
                    rect.moveLeft(mv)
            """

            rqt = self.tab_close_button_rect(rect)
            if not self.rect().contains(rqt):
                # would be nice to optimise by setting
                # a visible start-end at which to break
                #        v       v
                # -------[-------]-------
                continue


            # x,y,r,t = rect.getCoords()

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
            rqt.adjust(0,a,0,-a)

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
        rect = e.rect()
        visible_tabs = []
        for i in range(self.count()):
            if rect.contains(self.tabRect(i)):
                visible_tabs.append(i)

        p = QtGui.QPainter(self)
        p.setPen(self.pen)
        p.setBrush(self.brush)
        for i in visible_tabs:
            text = self.tabData(i)['name']
            tab_rect = self.tabRect(i)
            p.drawText(tab_rect, text)
    #     print rect
    #     i = self.tabAt(rect.center())
    #     text = self.tabText(i)
    #     # p.begin(self)
    #     # p.end()

    """
    # TEMP init values
    paintWithOffsets = False
    dragInProgress = False
    tabList = []
    verticalTabs = lambda shape: pass
    """
    def cpppaintEvent(self, e):
        """
        Pure reimplementation of
        QTabBar::paintEvent from qtabbar.cpp
        """
        # Q_D(QTabBar); # no idea
        optTabBase = QtWidgets.QStyleOptionTabBarBase()
        # no access to QTabBarPrivate
        # QTabBarPrivate::initStyleBaseOption(&optTabBase, this, size());
        p = QtWidgets.QStylePainter(self)

        # initialise some values:
        selected = -1
        cutLeft = -1
        cutRight = -1
        vertical = False # TEMP

        vertical = verticalTabs(self.shape()); # no verticalTabs
        cutTabLeft = QtWidgets.QStyleOptionTab()
        cutTabRight = QtWidgets.QStyleOptionTab()
        selected = self.currentIndex()

        if self.dragInProgress:
            selected = self.pressedIndex
        scrollRect = self.normalizedScrollRect()

        for i in range(self.count()):
            optTabBase.tabBarRect |= self.tabRect(i)

        optTabBase.selectedTabRect = self.tabRect(selected)

        if self.drawBase():
            p.drawPrimitive(QtWidgets.QStyle.PE_FrameTabBarBase, optTabBase)

        for i in range(self.count()):
            tab = QtWidgets.QStyleOptionTab()
            self.initStyleOption(tab, i)
            if self.paintWithOffsets and self.tabList[i].dragOffset != 0:
                if vertical:
                    tab.rect.moveTop(tab.rect.y() + self.tabList[i].dragOffset)
                else:
                    tab.rect.moveLeft(tab.rect.x() + self.tabList[i].dragOffset)
            if not tab.state and QtWidgets.QStyle.State_Enabled:
                tab.palette.setCurrentColorGroup(QtGui.QPalette.Disabled);

            # If this tab is partially obscured, make a note of it so that we can pass the information
            # along when we draw the tear.
            tabRect = self.tabList[i].rect
            tabStart = tabRect.top() if vertical else tabRect.left()
            tabEnd =  tabRect.bottom() if vertical else tabRect.right()
            if tabStart < (scrollRect.left() + self.scrollOffset):
                cutLeft = i
                cutTabLeft = tab
            elif tabEnd > (scrollRect.right() + self.scrollOffset):
                cutRight = i
                cutTabRight = tab

            # Don't bother drawing a tab if the entire tab is outside of the visible tab bar.
            out_of_width_bounds = not vertical and (tab.rect.right() < 0
                                  or tab.rect.left() > self.width())
            out_of_height_bounds = vertical and (tab.rect.bottom() < 0
                                   or tab.rect.top() > self.height())
            if out_of_width_bounds or out_of_height_bounds:
                continue

            optTabBase.tabBarRect |= tab.rect
            if i == selected:
                continue

            p.drawControl(QtWidgets.QStyle.CE_TabBarTab, tab)

        # Draw the selected tab last to get it "on top"
        if selected >= 0:
            tab = QtWidgets.QStyleOptionTab()
            self.initStyleOption(tab, selected)
            if self.paintWithOffsets and self.tabList[selected].dragOffset != 0:
                if vertical:
                    tab.rect.moveTop(tab.rect.y() + self.tabList[selected].dragOffset)
                else:
                    tab.rect.moveLeft(tab.rect.x() + self.tabList[selected].dragOffset)
            if not self.dragInProgress:
                p.drawControl(QtWidgets.QStyle.CE_TabBarTab, tab)
            else:
                taboverlap = self.style().pixelMetric(QtWidgets.QStyle.PM_TabBarTabOverlap, 0, self)
                if self.verticalTabs(self.shape()):
                    self.movingTab.setGeometry(tab.rect.adjusted(0, -taboverlap, 0, taboverlap))
                else:
                    self.movingTab.setGeometry(tab.rect.adjusted(-taboverlap, 0, taboverlap, 0))

        # Only draw the tear indicator if necessary. Most of the time we don't need too.
        if self.leftB.isVisible() and cutLeft >= 0:
            cutTabLeft.rect = self.rect()
            cutTabLeft.rect = self.style().subElementRect(QtWidgets.QStyle.SE_TabBarTearIndicatorLeft, cutTabLeft, self)
            p.drawPrimitive(QtWidgets.QStyle.PE_IndicatorTabTearLeft, cutTabLeft)

        if self.rightB.isVisible() and cutRight >= 0:
            cutTabRight.rect = self.rect()
            cutTabRight.rect = self.style().subElementRect(QtWidgets.QStyle.SE_TabBarTearIndicatorRight, cutTabRight, self)
            p.drawPrimitive(QtWidgets.QStyle.PE_IndicatorTabTearRight, cutTabRight)

    def mouseReleaseEvent(self, e):
        self.tab_pressed = False
        super(Tabs, self).mouseReleaseEvent(e)

    def mousePressEvent(self, e):
        """
        If clicking on close buttons
        """
        if e.button() == QtCore.Qt.LeftButton:
            self.tab_pressed = True
            pt = e.pos()
            i = self.tabAt(pt)
            data = self.tabData(i)
            data['dragStartPosition'] = pt
            self.setTabData(i, data)
            self.pressedIndex = i

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
                    rqt = self.tab_close_button_rect(rect)
                    if rqt.contains(pt):
                        print 'clicked close on tab %s %s' % (i, self.tabText(i))
                        self.safe_remove_tab(i)
                        return

        # if not returned, handle clicking on tab
        return super(Tabs, self).mousePressEvent(e)

    def mouseMoveEvent(self, event):
        """
        TODO: make close buttons follow tabs when they're moving!
        """
        if event.buttons() == QtCore.Qt.LeftButton:
            if self.pressedIndex != self.currentIndex():
                self.pressedIndex = self.currentIndex()
            data = self.tabData(self.pressedIndex)
            start_pos = data['dragStartPosition']
            dragDistance = (event.pos().x() - start_pos.x())
            data['dragDistance'] = dragDistance
            self.setTabData(self.pressedIndex, data)
            # print(dragDistance)
            # print self.pressedIndex
            # print('WARNING: HAVE WE UPDATED self.pressedIndex?')
        super(Tabs, self).mouseMoveEvent(event)

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
        if self.tabs.get('cursor_pos') is not None:
            cursor = self.editor.textCursor()
            pos = self.tabs['cursor_pos']
            cursor.setPosition(pos)
            self.editor.setTextCursor(cursor)

    def save_text_in_tab(self):
        """
        Store the editor's current text
        in the current tab
        """
        # print 'changed, saving text in tab. we want this to be the user entering text only!'

        if self.editor.uid == self.tabs['uuid']:
            if self.tabs.get('state') != 'not_saved':
                self.tabs['old_text'] = self.tabs['text']
                self.tabs['state'] = 'not_saved'
                self.tabs.repaint()
            elif self.tabs.get('old_text') is not None:
                if self.tabs['old_text'] == self.editor.toPlainText():
                    self.tabs['state'] = 'saved'
                    self.tabs.repaint()

            self.tabs['text'] = self.editor.toPlainText()
            self.tabs['cursor_pos'] = self.editor.textCursor().position()

    @QtCore.Slot(int, int)
    def tab_restrict_move(self, from_index, to_index):
        """
        Prevents tabs from being moved beyond the +
        new tab button.
        """
        if from_index >= self.tabs.count()-1:
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
