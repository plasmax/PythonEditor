"""
This module provides a subclass of QTabBar (Tabs)
and custom QWidget (TabEditor) that looks like a
QTabWidget, the difference being that it contains
a single Editor widget, with the text data for each
tab being stored in its tabData.
"""

import time
import os
import uuid
from functools import partial

from PythonEditor.ui.Qt.QtCore import (
    QSize, QEvent, QPoint, Signal,
    QTimer, Slot, Qt)

from PythonEditor.ui.Qt.QtGui import (
    QPainter, QColor, QPalette, QPen,
    QBrush, QClipboard, QCursor,
    QTextCursor)

from PythonEditor.ui.Qt.QtWidgets import (
    QAbstractButton, QStyle, QStyleOption,
    QTabBar, QToolButton, QMenu,
    QLineEdit, QMessageBox, QWidget,
    QVBoxLayout, QHBoxLayout, QComboBox)

from PythonEditor.utils import save
from PythonEditor.utils.debug import debug
from PythonEditor.ui.features import autosavexml
from PythonEditor.ui import editor


TAB_STYLESHEET = """
QTabBar::tab {
    height: 24px;
    min-width: 100px;
}

QTabBar QToolButton {
    background-color: rgba(255, 255, 255, 0);
}

QTabBar QToolButton::right-arrow:enabled {
    background-color: rgba(255, 255, 255, 0);
    border:0;
}

QTabBar QToolButton::right-arrow:disabled {
   background-color: rgba(255, 255, 255, 0);
   border:0;
}

QTabBar QToolButton::left-arrow:enabled {
    background-color: rgba(255, 255, 255, 0);
    border:0;
}

QTabBar QToolButton::left-arrow:disabled {
    background-color: rgba(255, 255, 255, 0);
    border:0;
}

QTabBar::tear {
    width: 0px;
    border: none;
}

QToolButton {
    color: grey;
    border-radius: 0px;
    padding: 2px;
}

QToolButton:hover {
    border-radius: 1px;
    padding: 0px;
    color: palette(highlight);
}
"""


# more stylesheet examples
"""
QPushButton,QToolButton {

  background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #fdfbf7, stop: 1 #cfccc7);
  border-width: 1px;
  border-color: #8f8f91;
  border-style: solid;
  border-radius: 3px;
  padding: 4px;
  padding-left: 5px;
  padding-right: 5px;
}

QToolButton[popupMode="1"] {

  padding-right: 18px;
}

QToolButton::menu-button {

  border-width: 1px;
  border-color: #8f8f91;
  border-style: solid;
  border-top-right-radius: 3px;
  border-bottom-right-radius: 3px;
  /* 16px width + 2 * 1px for border = 18px allocated above */
  width: 16px;
}

QPushButton:hover,QToolButton:hover {

  border-top-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #b2afaa, stop: 0.5 #4847a1, stop: 1 #7e7cb6);
  border-radius: 1px;
  border-top-width: 3px;
  border-bottom-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #7e7cb6, stop: 0.5 #4847a1, stop: 1 #b2afaa);
  border-bottom-width: 3px;
  background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #e4e0e1, stop: 1 #cfcbcd);
}

QPushButton:pressed,QToolButton:pressed {

  background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #cfcbcd, stop: 1 #e4e0e1);
  border-width: 1px;
  border-color: #8f8f91;
}

QPushButton:focus,QToolButton:focus {

  outline: none;
}
"""

class CloseButton(QAbstractButton):
    close_clicked_signal = Signal(QPoint)
    def __init__(self, parent=None):
        super(CloseButton, self).__init__(
            parent=parent
        )
        self.setFocusPolicy(Qt.NoFocus)
        self.setToolTip('Close Tab')
        self.resize(self.sizeHint())
        self.tab_saved = False

    def sizeHint(self):
        self.ensurePolished()
        width = self.style().pixelMetric(
            QStyle.PM_TabCloseIndicatorWidth,
            None,
            self
        )
        height = self.style().pixelMetric(
            QStyle.PM_TabCloseIndicatorHeight,
            None,
            self
        )
        return QSize(width, height)

    def enterEvent(self, event):
        if self.isEnabled():
            self.update()
        super(CloseButton, self).enterEvent(event)

    def leaveEvent(self, event):
        if self.isEnabled():
            self.update()
        super(CloseButton, self).leaveEvent(event)

    def mousePressEvent(self, event):
        super(CloseButton, self).mousePressEvent(event)
        parent_pos = self.mapToParent(event.pos())
        self.close_clicked_signal.emit(parent_pos)

    def paintEvent(self, event):
        """Adapted from qttabbar.cpp"""
        p = QPainter(self)
        opt = QStyleOption()
        opt.initFrom(self)
        opt.state |= QStyle.State_AutoRaise
        hovered = False
        if (self.isEnabled()
            and self.underMouse()
            and (not self.isChecked())
            and (not self.isDown())
            ):
            hovered = True
            opt.state |= QStyle.State_Raised
        if self.isChecked():
            opt.state |= QStyle.State_On
        if self.isDown():
            opt.state |= QStyle.State_Sunken

        if isinstance(
                self.parent(),
                QTabBar
            ):
            tb = self.parent()
            index = tb.currentIndex()
            BP = QTabBar.ButtonPosition
            position = BP(
                tb.style().styleHint(
                QStyle.SH_TabBar_CloseButtonPosition,
                opt,
                tb)
            )
            tab_button = tb.tabButton(index, position)
            if (self == tab_button):
                opt.state |= QStyle.State_Selected

        self.style().drawPrimitive(
            QStyle.PE_IndicatorTabClose,
            opt,
            p,
            self
        )

        # the below is all good, but wait
        # until 'saved' status is properly
        # locked down.
        """
        if self.tab_saved or hovered:
            self.style().drawPrimitive(
            QStyle.PE_IndicatorTabClose, opt, p, self)
        else:
            font = p.font()
            font.setPointSize(9)
            font.setBold(True)
            p.setFont(font)
            rect = self.rect()
            rect.adjust(0,-1,0,0)

            palette = self.palette()
            # brush = QBrush(
            #     QColor(0.1, 0.1, 0.1, 1),
            #     Qt.SolidPattern
            #     )
            # palette.setBrush(
            #     QPalette.ColorRole.Text,
            #     brush
            #     )
            # palette.setBrush(
            #     QPalette.ColorRole.BrightText,
            #     brush
            #     )

            # set colour to darker (maybe adjust palette)
            self.style().drawItemText(p, rect, 0, palette, True, unicode(' o'))
        """


class Tabs(QTabBar):
    """
    Make tabs fast by overriding the
    paintEvent to draw close buttons.

    Current tab data can be easily
    indexed out of this class via Tabs[key].

    FIXME: This is a GUI class. The data management
    should happen within a data model. This class
    should only serve as a view into that model,
    to permit other views to similarly display the
    model's content.
    """
    pen = QPen()
    brush = QBrush()
    mouse_over_rect = False
    over_button = -1
    start_move_index = -1

    # for autosave purposes:
    contents_saved_signal   = Signal(str)
    # in case we receive a ctrl+shift+w signal
    # to close the tab:
    tab_close_signal        = Signal(str)
    tab_renamed_signal      = Signal(
                                str,
                                str,
                                str,
                                str,
                                object
                              )
    tab_repositioned_signal = Signal(
                                int,
                                int
                              )
    reset_tab_signal        = Signal()

    def __init__(self, parent=None):
        super(Tabs, self).__init__(parent)

        self.tab_pressed = False
        self.pressed_uid = ''
        self._hovered_index = -2

        self.setMovable(True)
        self.setMouseTracking(True)
        self.setExpanding(False)
        self.setSelectionBehaviorOnRemove(QTabBar.SelectPreviousTab)
        self.setStyleSheet(TAB_STYLESHEET)

        # # a stack for navigating positions
        # # `list` of `tuples`
        # # [(`str` tab_uid, `int` cursor_pos),]
        # self.cursor_previous = []
        # self.cursor_next = []

        cb = CloseButton(self)
        self.tab_close_button = cb
        cb.hide()
        cb.close_clicked_signal.connect(
            self.clicked_close
        )

    @Slot(str)
    def new_tab(self, tab_name=None, tab_data={}):
        """
        Creates a new tab.
        """
        index = self.currentIndex()+1

        if (tab_name is None
                or not tab_name):
            tab_name = 'Tab {0}'.format(index)

        self.insertTab(index, tab_name)
        data = {
            'uuid'  : str(uuid.uuid4()),
            'name'  : tab_name,
            'text'  : '',
            'path'  : '',
            'date'  : '',
            'saved' : False,
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
            raise KeyError(
                'No tab data available for index %i.' % index
            )

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
        self.setTabData(index, tab_data)

    def tab_only_rect(self):
        """
        self.rect() without the <> buttons.
        """
        rect = self.rect()
        lB, rB = [
            c for c in self.children()
            if isinstance(c, QToolButton)
        ]
        side_button_width = lB.width()+rB.width()+15
        rect.adjust(0,0, -side_button_width, 0)
        return rect

    def event(self, event):
        try:
            # Check class (after reload, opening a new window, etc)
            # this can raise TypeError:
            # super(type, obj): obj must be an instance or subtype of type
            if not issubclass(Tabs, self.__class__):
                return False
        except TypeError:
            return False

        try:
            QE = QEvent
        except AttributeError:
            return True

        if event.type() in [
            QE.HoverEnter,
            QE.HoverMove,
            QE.HoverLeave,
            QE.Paint,
            ]:
            self.handle_close_button_display(event)

        elif event.type() == QEvent.ToolTip:
            pos = self.mapFromGlobal(
                self.cursor().pos()
            )
            if self.rect().contains(pos):
                i = self.tabAt(pos)
                data = self.tabData(i)
                if data is not None:
                    path = data.get('path')
                    if path:
                        self.setTabToolTip(
                            i,
                            path
                        )
                    else:
                        self.setTabToolTip(
                            i,
                            data.get('name')
                        )

        return super(Tabs, self).event(event)

    def handle_close_button_display(self, e):

        if self.tab_pressed:
            if self.tab_close_button.isVisible():
                self.tab_close_button.hide()
            return

        if e.type() in [
            e.HoverEnter,
            e.MouseButtonRelease
            ]:
            pos = e.pos()
            self._hovered_index = i = self.tabAt(pos)
            self.tab_close_button.show()
            self.tab_close_button.raise_()
            self.move_tab_close_button(pos)

            data = self.tabData(i)
            if data is not None:
                ts = data.get('saved')
                tcb = self.tab_close_button
                tcb.tab_saved = ts

        elif e.type() == QEvent.HoverMove:
            pos = e.pos()
            i = self.tabAt(pos)
            if i != self._hovered_index:
                self.tab_close_button.show()
                self.move_tab_close_button(pos)
                self._hovered_index = i

                data = self.tabData(i)
                if data is not None:
                    ts = data.get('saved')
                    tcb = self.tab_close_button
                    tcb.tab_saved = ts

        elif e.type() == QEvent.HoverLeave:
            self.tab_close_button.hide()

        elif e.type() == QEvent.Paint:
            if hasattr(self, 'name_edit'):
                if self.name_edit.isVisible():
                    self.tab_close_button.hide()
                    return
            pos = self.mapFromGlobal(
                self.cursor().pos()
            )

            if not self.rect().contains(pos):
                return

            if not self.tab_only_rect(
                ).contains(pos):
                return

            i = self.tabAt(pos)
            if (i != self._hovered_index):
                self.move_tab_close_button(pos)
                self._hovered_index = i

            if self.tab_close_button.isVisible():
                data = self.tabData(i)
                if data is not None:
                    ts = data.get('saved')
                    tcb = self.tab_close_button
                    tcb.tab_saved = ts

    def move_tab_close_button(self, pos):
        i = self.tabAt(pos)
        rect = self.tabRect(i)
        btn = self.tab_close_button
        x = rect.right()-btn.width()-2
        y = rect.center().y()-(btn.height()/2)
        if i != self.currentIndex():
            y += 2
        btn_pos = QPoint(x, y)

        btn.move(btn_pos)
        btn.raise_()

        if not self.tab_only_rect(
            ).contains(btn_pos):
            btn.hide()
        elif not self.tab_pressed:
            btn.show()

    def mousePressEvent(self, event):
        """
        """
        # this doesn't cover wacom...
        # might need tabletPressEvent
        if event.button() == Qt.LeftButton:
            self.tab_pressed = True
            pt = event.pos()
            i = self.tabAt(pt)
            self.pressedIndex = i
            self.start_move_index = i
            data = self.tabData(i)
            if data is not None:
                self.pressed_uid = data['uuid']
            self.dragStartPosition = pt

            # handle name edit still being visible
            if hasattr(self, 'name_edit'):
                try:
                    if self.name_edit.isVisible():
                        ti = self.name_edit.tab_index
                        if ti != i:
                            self.rename_tab()
                except RuntimeError:
                    # likely that the lineedit
                    # has been deleted
                    del self.name_edit

        # if not returned, handle clicking on tab
        return super(Tabs, self
            ).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """
        TODO: make close buttons follow tabs
        when they're moving!
        """
        if self.count() == 0:
            return
        if event.buttons() == Qt.LeftButton:
            i = self.currentIndex()
            if (not hasattr(self, 'pressedIndex')
                or self.pressedIndex != i):
                self.pressedIndex = i
            data = self.tabData(self.pressedIndex)
            if data['uuid'] != self.pressed_uid:
                debug('wrong tab!')

        return super(
            Tabs, self
            ).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.tab_pressed = False
        i = self.tabAt(event.pos())
        if event.button() == Qt.LeftButton:
            if i == -1:
                i = self.currentIndex()
            if (i != self.start_move_index):
                self.tab_repositioned_signal.emit(
                    i,
                    self.start_move_index
                )
            self.handle_close_button_display(event)

        elif event.button() == Qt.RightButton:
            menu = QMenu()

            rename = partial(self._show_name_edit, i)
            menu.addAction('Rename', rename)

            move_to_first = partial(self.move_to_first, i)
            menu.addAction('Move Tab to First', move_to_first)

            move_to_last = partial(self.move_to_last, i)
            menu.addAction('Move Tab to Last', move_to_last)

            close_tab_func = partial(self.removeTab, i)
            menu.addAction('Close Tab', close_tab_func)

            copy_file_path = partial(self.copy_tab_file_path, i)
            menu.addAction('Copy File Path', copy_file_path)

            # Other ideas (TODO)
            """
            menu.addAction('Close Other Tabs', )
            menu.addAction('Close Tabs to Right', )
            menu.addAction('Close Tabs to Left', )
            menu.addAction('Pin Tab', )
            """

            menu.exec_(QCursor().pos())

        elif event.button() == Qt.MiddleButton:
            if i != -1:
                self.removeTab(i)

        return super(
            Tabs, self
            ).mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.show_name_edit(event)
        return super(
            Tabs, self
            ).mouseDoubleClickEvent(event)

    def show_name_edit(self, event):
        """
        Shows a QLineEdit widget where the tab
        text is, allowing renaming of tabs.
        """
        try:
            self.rename_tab()
        except RuntimeError: # likely that the lineedit has been deleted
            del self.name_edit
            return

        index = self.tabAt(event.pos())
        self._show_name_edit(index)

    def _show_name_edit(self, index):
        """
        Shows a QLineEdit widget where the tab
        text is, allowing renaming of tabs.
        """
        rect = self.tabRect(index)

        label = self.tabText(index)
        self.renaming_label = label

        self.tab_text = label
        self.tab_index = index

        self.name_edit = QLineEdit(self)
        self.name_edit.resize(
            rect.width(),
            rect.height()-7
        )
        self.name_edit.tab_index = index
        self.name_edit.tab_text = label
        self.name_edit.editingFinished.connect(
            self.rename_tab
        )
        self.name_edit.setText(
            label.strip()
        )
        self.name_edit.selectAll()
        self.name_edit.show()
        self.name_edit.raise_()
        p = rect.topLeft()
        self.name_edit.move(
            p.x(),
            p.y()+5
        )

        self.name_edit.setFocus(
            Qt.MouseFocusReason
        )

    def copy_tab_file_path(self, index):
        """
        Copy the current tab's file path
        (if it has one) to the clipboard.
        """
        data = self.tabData(index)
        path = data.get('path')
        if path is None or not path.strip():
            print('No file path for "{0}".'.format(
                data['name'])
            )
            return
        clipboard = QClipboard()
        clipboard.setText(path)
        print('Path copied to clipboard:')
        print(path)

    def move_to_first(self, index):
        """
        Move the current tab to the first position.
        """
        self.setCurrentIndex(0)
        self.moveTab(index, 0)
        self.setCurrentIndex(0)
        self.tab_repositioned_signal.emit(index, 0)

    def move_to_last(self, index):
        """
        Move the current tab to the last position.
        """
        last = self.count()-1
        self.setCurrentIndex(last)
        self.moveTab(index, last)
        self.setCurrentIndex(last)
        self.tab_repositioned_signal.emit(index, last)

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

        if self.renaming_label == label:
            return

        # FIXME: if the tab is not
        # positioned to the right,
        # this can cause a jump.
        self.setTabText(index, label)

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

    @Slot()
    def remove_current_tab(self):
        self.removeTab(self.currentIndex())

    @Slot(QPoint)
    def clicked_close(self, pos):
        for i in range(self.count()):
            rect = self.tabRect(i)
            if rect.contains(pos):
                label = self.tabText(i)
                self.removeTab(i)

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
                # can't be sure it's saved
                # if it has no path
                data['saved'] = False
            elif not os.path.isfile(path):
                # can't be sure it's saved
                # if path doesn't exist
                data['saved'] = False
            else:
                with open(path, 'r') as f:
                    saved_text = f.read()
                if not saved_text == text:
                    data['saved'] = False

            saved = (data.get('saved') is True)
            if not saved:
                i = index
                if not self.prompt_user_to_save(i):
                    return

        super(Tabs, self).removeTab(index)

        self.tab_close_signal.emit(data['uuid'])

    def prompt_user_to_save(self, index):
        """ Ask the user if they wish to close
        a tab that has unsaved contents.
        """
        name = self.tabText(index)
        msg_box = QMessageBox()
        msg_box.setWindowTitle('Save changes?')
        msg_box.setText(
            '%s has not been saved to a file.'
            % name
        )
        msg_box.setInformativeText(
            'Do you want to save your changes?'
        )
        buttons = (
            msg_box.Save
            | msg_box.Discard
            | msg_box.Cancel
        )
        msg_box.setStandardButtons(buttons)
        msg_box.setDefaultButton(msg_box.Save)
        ret = msg_box.exec_()

        user_cancelled = (ret == msg_box.Cancel)

        if (ret == msg_box.Save):
            data = self.tabData(index)
            path = save.save(
                data['text'],
                data['path']
            )
            if path is None:
                user_cancelled = True

        if user_cancelled:
            return False

        return True


class TabEditor(QWidget):
    """
    A psuedo-QTabWidget that contains
    a QTabBar and a single Editor.
    """
    tab_switched_signal = Signal()

    def __init__(self, parent=None):
        super(TabEditor, self).__init__(parent)
        if parent is not None:
            self.setParent(parent)

        self.setLayout(
            QVBoxLayout(self)
        )
        self.layout().setContentsMargins(0,0,0,0)

        self.tab_widget = QWidget()
        twl = QHBoxLayout(
            self.tab_widget
        )
        self.tab_widget_layout = twl
        self.tab_widget_layout.setContentsMargins(
            0,0,0,0
        )

        lb = QToolButton()
        self.tab_left_button = lb
        lb.setArrowType(Qt.LeftArrow)
        lb.setAutoRaise(True)
        lb.setToolTip('Go to previous tab.')
        self.tab_widget_layout.addWidget(lb)
        self.tab_left_button.clicked.connect(self.tab_left)

        self.tabs = Tabs()
        self.tab_widget_layout.addWidget(self.tabs)

        rb = QToolButton()
        self.tab_right_button = rb
        rb.setArrowType(Qt.RightArrow)
        rb.setAutoRaise(True)
        rb.setToolTip('Go to next tab.')
        self.tab_widget_layout.addWidget(rb)
        self.tab_right_button.clicked.connect(self.tab_right)

        # add corner buttons
        tb = QToolButton()
        self.tab_list_button = tb
        tb.setArrowType(Qt.DownArrow)
        tb.setToolTip(
            'Click for a list of tabs.'
        )
        tb.setAutoRaise(True)
        self.tab_list_button.clicked.connect(
            self.show_tab_menu
        )

        nb = QToolButton()
        self.new_tab_button = nb
        nb.setToolTip(
            'Click to add a new tab.'
        )
        nb.setText('+')
        nb.setAutoRaise(True)
        self.new_tab_button.clicked.connect(
            self.new_tab
        )

        for button in [
                self.new_tab_button,
                self.tab_list_button
            ]:
            self.tab_widget_layout.addWidget(button)

        self.editor = editor.Editor(
            parent=self,
            handle_shortcuts=False
        )

        for widget in self.tab_widget, self.editor:
            self.layout().addWidget(widget)

        # Give the autosave a chance to load all
        # tabs before connecting signals between
        # tabs and editor.
        QTimer.singleShot(
            0,
            self.connect_signals
        )

        self.setStyleSheet(TAB_STYLESHEET)

    def connect_signals(self):
        """
        We probably want to run this after tabs
        are loaded.
        """
        self.tabs.currentChanged.connect(
            self.set_editor_contents
        )
        self.tabs.currentChanged.connect(
            self.check_hide_arrows
        )
        self.tabs.tab_close_signal.connect(
            self.empty_if_last_tab_closed
        )

        self.editor.cursorPositionChanged.connect(
            self.store_cursor_position
        )
        self.editor.selectionChanged.connect(
            self.store_selection
        )

        # this is something we're going to want
        # only when tab already set (and not
        # when switching)
        self.editor.text_changed_signal.connect(
            self.save_text_in_tab
        )

    def check_hide_arrows(self, index):
        if index == 0:
            self.tab_left_button.hide()
        elif index == self.tabs.count()-1:
            self.tab_right_button.hide()
        else:
            if not self.tab_right_button.isVisible():
                self.tab_right_button.show()
            if not self.tab_left_button.isVisible():
                self.tab_left_button.show()

    def tab_left(self):
        i = self.tabs.currentIndex()-1
        if i >= 0:
            self.tabs.setCurrentIndex(i)

    def tab_right(self):
        i = self.tabs.currentIndex()+1
        if i <= self.tabs.count():
            self.tabs.setCurrentIndex(i)

    def show_tab_menu(self):
        """Show a QComboBox with a list
        of all the tabs, allowing you to
        scroll through all tabs easily and
        search by name."""
        current_index = self.tabs.currentIndex()
        tab_list = [self.tabs.tabText(i)
        for i in range(self.tabs.count())]

        class TabCombo(QComboBox):
            def __init__(self, parent=None):
                super(TabCombo, self).__init__(parent)
                self.setWindowFlags(Qt.FramelessWindowHint)
                self.setSizeAdjustPolicy(QComboBox.AdjustToContents)
                self.setEditable(True)
            def focusOutEvent(self, event):
                super(TabCombo, self).focusOutEvent(event)
                if event.reason() == Qt.FocusReason.ActiveWindowFocusReason:
                    self.close()
            def keyPressEvent(self, event):
                super(TabCombo, self).keyPressEvent(event)
                if event.key() == Qt.Key_Escape:
                    self.close()

        self._tab_combo = TabCombo()
        self._tab_combo.addItems(tab_list)
        self._tab_combo.adjustSize()
        self._tab_combo.setCurrentIndex(current_index)

        self._tab_combo.show()
        self._tab_combo.resize(200, 30)
        self._tab_combo.move(QCursor().pos())
        self._tab_combo.setFocus(Qt.MouseFocusReason)
        self._tab_combo.lineEdit().selectAll()
        self._tab_combo.currentIndexChanged.connect(
            self.tabs.setCurrentIndex)
        # self._tab_combo.lineEdit().setText('')
        # self._tab_combo.completer().complete()

    def new_tab(self, tab_name=None, tab_data={}):
        return self.tabs.new_tab(
            tab_name=tab_name,
            tab_data=tab_data
            )

    def close_current_tab(self):
        raise NotImplementedError

    @Slot(str)
    def empty_if_last_tab_closed(self, uid):
        if self.tabs.count() == 0:
            self.editor.setPlainText('')

    @Slot(int)
    def set_editor_contents(self, index):
        """
        Set editor contents to the data
        found in tab #index
        """
        data = self.tabs.tabData(index)

        if not data:
            # this will be a new
            # empty tab, ignore.
            return

        text = data['text']

        if text is None or not text.strip():
            path = data.get('path')
            if path is None:
                text = ''
            elif not os.path.isfile(path):
                text = ''
            else:
                with open(path, 'r') as f:
                    text = f.read()
                data['text'] = text

        # collect data before setting editor text
        cursor_pos = self.tabs.get('cursor_pos')
        selection = self.tabs.get('selection')

        self.editor.setPlainText(text)

        if cursor_pos is not None:
            block_pos, cursor_pos = cursor_pos

            # set first block visible
            cursor = self.editor.textCursor()
            self.editor.moveCursor(cursor.End)
            cursor.setPosition(block_pos)
            self.editor.setTextCursor(cursor)

            # restore cursor position
            cursor = self.editor.textCursor()
            cursor.setPosition(cursor_pos)
            self.editor.setTextCursor(cursor)

        if selection is not None:
            # TODO: this won't restore a selection
            # that starts from below and selects
            # upwards :( (yet)
            cursor = self.editor.textCursor()
            has, start, end = selection
            if has:
                cursor.setPosition(
                    start,
                    QTextCursor.MoveAnchor
                )
                cursor.setPosition(
                    end,
                    QTextCursor.KeepAnchor
                )
            self.editor.setTextCursor(cursor)
        self.editor.setFocus(Qt.MouseFocusReason)

        # for the autosave check_document_modified
        self.tab_switched_signal.emit()

    def store_cursor_position(self):
        editor = self.editor
        cursor = editor.textCursor()
        block = editor.firstVisibleBlock()
        self.tabs['cursor_pos'] = (
            block.position(),
            cursor.position()
            )

    def store_selection(self):
        tc = self.editor.textCursor()
        status = (tc.hasSelection(),
                  tc.selectionStart(),
                  tc.selectionEnd())
        self.tabs['selection'] = status

    def save_text_in_tab(self):
        """
        Store the editor's current text
        in the current tab.
        Strangely appears to be called twice
        on current editor's textChanged and
        backspace key...
        """
        if self.tabs.count() == 0:
            self.new_tab()

        saved = self.tabs.get('saved')
        original_text = self.tabs.get('original_text')
        if saved and not original_text:
            # keep original text in case
            # revert is required
            text = self.tabs['text']
            self.tabs['original_text'] = text
            self.tabs['saved'] = False
            self.tabs.repaint()
        elif original_text is not None:
            text = self.editor.toPlainText()
            if original_text == text:
                self.tabs['saved'] = True
                self.tabs.repaint()

        self.tabs['text'] = self.editor.toPlainText()
