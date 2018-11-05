"""
A nicer solution using a single editor and
a subclassed QTabBar.

TODO:
 x update the tab dict['text'] on every keypress
 - properly save
    ~ pick the dict data up with a background thread
 - draw proper looking, application native close buttons
 - ctrl + shift + n new tab
 - check for differences in tabs
 - work without PythonEditorHistory.xml

 # Keep the single responsibility principle in mind!

"""

import time
import os
import hashlib
import uuid
from PythonEditor.utils import save
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

    # for autosave purposes:
    reset_tab_signal = QtCore.Signal()
    tab_close_signal = QtCore.Signal(str) # in case we receive a ctrl+shift+w signal to close the tab
    tab_switched_signal = QtCore.Signal(int, int, bool)
    contents_saved_signal = QtCore.Signal(object)
    tab_moved_signal = QtCore.Signal(object, int)
    tab_renamed_signal = QtCore.Signal(str, str, str, str, object)

    def __init__(self, *args):
        super(Tabs, self).__init__(*args)
        self.tab_pressed = False
        self.setStyleSheet(TAB_STYLESHEET)
        self.setMovable(True)

    @QtCore.Slot(str)
    def new_tab(self, tab_name=None, tab_data={}):
        """
        Creates a new tab.
        """
        index = self.currentIndex()+1

        if (tab_name is None
                or not tab_name):
            tab_name = 'Tab {0}     '.format(index)

        self.insertTab(index, tab_name)
        data = {
            'uuid'  :  str(uuid.uuid4()),
            'name'  :  tab_name,
            'text'  :  '',
            'path'  :  '',
            'date'  :  '',
            'saved' :  False,
        }
        data.update(**tab_data)
        self.setTabData(index, data)
        self.setCurrentIndex(index)

    def __getitem__(self, name):
        """
        Allow easy lookup for
        the current tab's data.
        """
        index = self.currentIndex()
        if index == -1:
            raise KeyError('No current tab.')

        data = self.tabData(index)
        if data is None:
            raise KeyError('No tab data available.')

        return data[name]

    def get(self, name):
        try:
            return self[name]
        except KeyError:
            return None

    def __setitem__(self, name, value):
        """
        Easily set current tab's value.
        """
        if self.count() == 0:
            return
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

    def paint_close_button(self, event):
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
        rect = event.rect()
        visible_tabs = []
        for i in range(self.count()):
            if rect.intersects(self.tabRect(i)): # needs to look for left and right bounds
                visible_tabs.append(i)

        # for i in range(self.count()-1):
        #     rect = self.tabRect(i)

        #     """
        #     # TODO: make buttons follow the tabs properly
        #     # when moving. This should also take into account
        #     # the tab that moves underneath
        #     if self.tab_pressed and i == self.pressedIndex:
        #         data = self.tabData(i)
        #         if data.get('dragDistance') is not None:
        #             dist = data['dragDistance']
        #             mv = rect.x()+dist
        #             rect.moveLeft(mv)
        #     """

        #     rqt = self.tab_close_button_rect(rect)
        #     if not self.rect().contains(rqt):
        #         # would be nice to optimise by setting
        #         # a visible start-end at which to break
        #         #        v       v
        #         # -------[-------]-------
        #         continue



        p = QtGui.QPainter()
        p.begin(self)
        p.setBrush(self.brush)
        for i in visible_tabs:
            rect = self.tabRect(i)
            rqt = self.tab_close_button_rect(rect)
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

            saved = self.tabData(i).get('saved')
            if not saved and not mouse_over:
                p.drawEllipse(rqt)
            else:
                # """
                p.drawLine(rqt.bottomLeft(), rqt.topRight())
                p.drawLine(rqt.topLeft(), rqt.bottomRight())
                # """
                """ # haven't yet figured out close button positioning.
                tc = QtWidgets.QStyle.PE_IndicatorTabClose
                opt = QtWidgets.QStyleOption()
                opt.initFrom(self)
                w = rect.width()
                h = rect.height()
                x,y,r,t = rect.getCoords()
                # x,y,r,t = rect.getRect()
                rect.setWidth(h)
                rect.moveRight(x)
                # rect.adjust(0,0,0,0)
                # print rect
                opt.rect = rect
                s = self.style()
                s.drawPrimitive(tc, opt, p)
                """

        p.end()

    def paintEvent(self, e):
        super(Tabs, self).paintEvent(e)
        self.paint_close_button(e)
        return # not currently painting own text
        rect = e.rect()
        visible_tabs = []
        for i in range(self.count()):
            if rect.intersects(self.tabRect(i)): # TODO: should get right or left extreme of tab
                visible_tabs.append(i)

        p = QtGui.QPainter(self)
        # p.begin(self)
        p.setPen(self.pen)
        p.setBrush(self.brush)
        for i in visible_tabs:
            data = self.tabData(i)
            text = data.get('name')
            if text is None:
                p.end()
                return
            tab_rect = self.tabRect(i)
            # font.setItalic() ?
            # p.setFont()
            p.drawText(tab_rect, text)
        p.end()

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
        if e.button() == QtCore.Qt.LeftButton: # this doesn't cover wacom...
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
                        self.removeTab(i)
                        return

        # if not returned, handle clicking on tab
        return super(Tabs, self).mousePressEvent(e)

    def mouseMoveEvent(self, event):
        """
        TODO: make close buttons follow tabs when they're moving!
        """
        if self.count() == 0:
            return
        if event.buttons() == QtCore.Qt.LeftButton:
            if self.pressedIndex != self.currentIndex():
                self.pressedIndex = self.currentIndex()
            data = self.tabData(self.pressedIndex)

            # when closing a tab, if the mouse is already pressed (e.g. in a tablet event)
            # we'll need to reinstate the dragStartPosition.
            try:
                start_pos = data['dragStartPosition']
            except KeyError:
                data['dragStartPosition'] = event.pos()
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
        self.name_edit.tab_text = label
        self.name_edit.editingFinished.connect(self.rename_tab)
        self.name_edit.setText(label.strip())
        self.name_edit.selectAll()

        self.setTabButton(index,
                          QtWidgets.QTabBar.LeftSide,
                          self.name_edit)

        self.name_edit.setFocus(QtCore.Qt.MouseFocusReason)

    def rename_tab(self):
        """
        Sets the label of the tab the QLineEdit was
        spawned over.
        """
        if not (hasattr(self, 'name_edit')
                and self.name_edit.isVisible()):
            return

        self.name_edit.hide()

        label = self.name_edit.text().strip()
        if not bool(label):
            label = self.name_edit.tab_text

        index = self.name_edit.tab_index
        button = self.tabButton(index, QtWidgets.QTabBar.LeftSide)

        self.setTabText(index, label+' '*5)
        self.setTabButton(index,
                          QtWidgets.QTabBar.LeftSide,
                          None)


        data = self.tabData(index)
        data['name'] = label
        self.tab_renamed_signal.emit(
            data['uuid'],
            data['name'],
            data['text'],
            str(index),
            data.get('path')
            )
        self.setTabData(index, data)

    @QtCore.Slot()
    def remove_current_tab(self):
        self.removeTab(self.currentIndex())

    def removeTab(self, index):
        """
        The only way to remove a tab.

        If the tab's 'saved' property is not set to True,
        the user will be prompted to save.

        Setting 'saved' to True can only happen via:
        A) actually saving the file, or
        B) loading a stored tab which is just a saved file
        with no autosave text contents.

        If the tab is removed, its uuid is emitted which will notify
        the autosave handler to also remove the autosave.
        """
        data = self.tabData(index)
        if not isinstance(data, dict):
            return

        text = data.get('text')
        has_text = False
        if hasattr(text, 'strip'):
            has_text = bool(text.strip())

        if has_text:
            path = data.get('path')

            if path is None:
                # can't be sure it's saved if it has no path
                data['saved'] = False
            elif not os.path.isfile(path):
                # can't be sure it's saved if path doesn't exist
                data['saved'] = False
            else:
                with open(path, 'r') as f:
                    saved_text = f.read()
                if not saved_text == text:
                    data['saved'] = False

            saved = (data.get('saved') is True)
            if not saved:
                if not self.prompt_user_to_save(index):
                    return

        super(Tabs, self).removeTab(index)

        self.tab_close_signal.emit(data['uuid'])

    def prompt_user_to_save(self, index):
        """
        Ask the user if they wish to close a tab
        that has unsaved contents.
        """
        name = self.tabText(index)
        msg_box = QtWidgets.QMessageBox()
        msg_box.setWindowTitle('Save changes?')
        msg_box.setText('%s has not been saved to a file.' % name)
        msg_box.setInformativeText('Do you want to save your changes?')
        buttons = msg_box.Save | msg_box.Discard | msg_box.Cancel
        msg_box.setStandardButtons(buttons)
        msg_box.setDefaultButton(msg_box.Save)
        ret = msg_box.exec_()

        user_cancelled = (ret == msg_box.Cancel)

        if (ret == msg_box.Save):
            data = self.tabData(index)
            path = save.save(data['text'], data['path'])
            if path is None:
                user_cancelled = True

        if user_cancelled:
            return False

        return True


class TabContainer(QtWidgets.QWidget):
    """
    Replacement QTabWidget
    Contains a QTabBar and a single Editor.
    """

    def __init__(self):
        super(TabContainer, self).__init__()

        self.setLayout(QtWidgets.QVBoxLayout(self))
        self.layout().setContentsMargins(0,0,0,0)

        self.tab_widget = QtWidgets.QWidget()
        self.tab_widget_layout = QtWidgets.QHBoxLayout(self.tab_widget)
        self.tab_widget_layout.setContentsMargins(0,0,0,0)
        self.tabs = Tabs()
        self.tab_widget_layout.addWidget(self.tabs)

        # add corner buttons
        tb = self.tab_list_button = QtWidgets.QToolButton() # want ascii v down arrow
        tb.setText('v') # you could set an icon instead of text
        tb.setToolTip('Click for a list of tabs.')
        tb.setAutoRaise(True)
        tb.setFixedSize(24, 24)
        self.tab_list_button.clicked.connect(self.show_tab_menu)

        nb = self.new_tab_button = QtWidgets.QToolButton()
        nb.setToolTip('Click to add a new tab.')
        # nb.setMaximumSize(QtCore.QSize(50, 10))
        nb.setText('+')  # you could set an icon instead of text
        nb.setAutoRaise(True)
        self.new_tab_button.clicked.connect(self.new_tab)

        for button in self.new_tab_button, self.tab_list_button:
            self.tab_widget_layout.addWidget(button)

        self.editor = editor.Editor(handle_shortcuts=False)

        for widget in self.tab_widget, self.editor:
            self.layout().addWidget(widget)

        """
        Give the autosave a chance to load all tabs
        before connecting signals between tabs and editor.
        """
        QtCore.QTimer.singleShot(0, self.post_init_load_contents)

    @QtCore.Slot()
    def post_init_load_contents(self):
        """
        Separate connecting Signals until after all tab data
        is loaded in order to speed up initial loading.
        Also setup editor with first tab text contents.
        """
        count = self.tabs.count()
        self.tabs.setCurrentIndex(count)
        current_index = self.tabs.currentIndex()
        if current_index != -1:
            self.set_editor_contents(current_index)
        self.connect_signals()

    def connect_signals(self):
        """
        We probably want to run this after tabs are loaded.
        """
        self.tabs.currentChanged.connect(self.set_editor_contents)
        self.tabs.tab_close_signal.connect(self.empty_if_last_tab_closed)
        self.editor.cursorPositionChanged.connect(self.store_cursor_position)
        self.editor.selectionChanged.connect(self.store_selection)

        # this is something we're going to want only
        # when tab already set (and not when switching)
        self.editor.text_changed_signal.connect(self.save_text_in_tab)

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

    def new_tab(self, tab_name=None, tab_data={}):
        return self.tabs.new_tab(tab_name=tab_name, tab_data=tab_data)

    def close_current_tab(self):
        raise NotImplementedError

    @QtCore.Slot(str)
    def empty_if_last_tab_closed(self, uid):
        if self.tabs.count() == 0:
            self.editor.setPlainText('')

    @QtCore.Slot(int)
    def set_editor_contents(self, index):
        """
        Set editor contents to the data
        found in tab #index
        """
        data = self.tabs.tabData(index)

        if not data:
            return # this will be a new empty tab, ignore.

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

        if self.tabs.get('cursor_pos') is not None:
            cursor = self.editor.textCursor()
            pos = self.tabs['cursor_pos']
            cursor.setPosition(pos)
            self.editor.setTextCursor(cursor)

        if self.tabs.get('selection') is not None:
            # TODO: this won't restore a selection that
            # starts from below and selects upwards :( (yet)
            has, start, end = self.tabs['selection']
            if not has:
                return
            cursor = self.editor.textCursor()
            cursor.setPosition(start, QtGui.QTextCursor.MoveAnchor)
            cursor.setPosition(end, QtGui.QTextCursor.KeepAnchor)
            self.editor.setTextCursor(cursor)

    def store_cursor_position(self):
        self.tabs['cursor_pos'] = self.editor.textCursor().position()

    def store_selection(self):
        tc = self.editor.textCursor()
        self.tabs['selection'] = (tc.hasSelection(),
                                  tc.selectionStart(),
                                  tc.selectionEnd())

    def save_text_in_tab(self):
        """
        Store the editor's current text
        in the current tab.
        Strangely appears to be called twice on current editor's textChanged and
        backspace key...
        """
        if self.tabs.count() == 0:
            self.new_tab()
            # self.tabs['uuid'] = self.editor.uuid

        if self.tabs.get('saved'):
            # keep original text in case revert is required
            self.tabs['original_text'] = self.tabs['text']
            self.tabs['saved'] = False
            self.tabs.repaint()
        elif self.tabs.get('original_text') is not None:
            if self.tabs['original_text'] == self.editor.toPlainText():
                self.tabs['saved'] = True
                self.tabs.repaint()

        self.tabs['text'] = self.editor.toPlainText()

        # fun but currently unused
        text = self.tabs['text']
        self.tabs['hash'] = hashlib.sha1(text).hexdigest()
        # print self.tabs['hash']


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
