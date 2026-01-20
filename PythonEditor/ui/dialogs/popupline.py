import re

from PythonEditor.ui.Qt.QtGui import *
from PythonEditor.ui.Qt.QtWidgets import *
from PythonEditor.ui.Qt.QtCore import *
from PythonEditor.utils.search import nonconsec_find
from PythonEditor.utils.goto import goto_position
from PythonEditor.utils.goto import goto_line


LINENO_ROLE = Qt.UserRole+4


class SymbolModel(QStandardItemModel):
    loading_complete = Signal(int)
    def __init__(self, parent=None):
        super(SymbolModel, self).__init__(parent=parent)
        self._previous_indent = 0

    def populate_from_editor(self, editor):
        self.editor = editor
        self.current_lineno = editor.textCursor().blockNumber()+1
        self.populate_flat()

    def populate_flat(self):
        row = 0
        for lineno, text, indent in self.get_symbols():
            item = QStandardItem(text)
            item.setData(lineno, role=LINENO_ROLE)
            self.appendRow([item])
            if lineno <= self.current_lineno:
                row += 1
        self.loading_complete.emit(row-1)

    def populate_hierarchical(self):
        parent = self
        previous_item = self
        for lineno, text, indent in self.get_symbols():
            item = QStandardItem(text.strip())
            item.setData(lineno, role=LINENO_ROLE)
            if indent==0:
                parent = self
                previous_item = item
            elif indent > self._previous_indent:
                parent = previous_item
            else:
                previous_item = item
            parent.appendRow([item])
            self._previous_indent = indent

    def get_symbols(self):
        whole_text = self.editor.toPlainText()
        for lineno, text in enumerate(whole_text.splitlines()):
            text = text.rstrip()
            indent = len(text)-len(text.lstrip(' '))
            if text.strip().startswith('def '):
                text = text.replace('def ', '')
            elif text.strip().startswith('class '):
                text = text.replace('class ', '')
            else:
                continue
            if text.endswith(':'):
                text = text[:-1]

            yield (lineno+1, text, indent)


class ProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(ProxyModel, self).__init__(parent=parent)
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._pattern = ''
        self.setFilterKeyColumn(0)

    def setFilterRegExp(self, pattern):
        self._pattern = str(pattern).lower()
        super(ProxyModel, self).setFilterRegExp(pattern)

    def filterAcceptsRow(self, row, parent):
        if not self._pattern:
            return True
        model = self.sourceModel()
        index = model.index(row, self.filterKeyColumn(), parent)
        found = self.index_match(index)
        return found

    def index_match(self, index):
        text = index.data(Qt.DisplayRole)
        needle = str(self._pattern).lower()
        haystack = str(text.strip()).lower()
        return nonconsec_find(needle, haystack, anchored=False)


class Popup(QWidget):
    def showEvent(self, event):
        super(Popup, self).showEvent(event)
        self.place_over_parent()

    def place_over_parent(self):
        parent = self.parent()
        self.resize(parent.width()/2, self.height())
        pos = parent.rect().center() - self.rect().center()
        pos = QPoint(pos.x(), 0)
        self.move(pos)


class CodeDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(CodeDelegate, self).__init__(parent=parent)
        self.filter_text = ''

    def sizeHint(self, option, index):
        size = super(CodeDelegate, self).sizeHint(option, index)
        size.setHeight(size.height()+6)
        return size

    def paint(self, painter, option, index):

        # don't draw the default focus border
        if option.state & QStyle.State_HasFocus:
            option.state &= ~ QStyle.State_HasFocus

        if not self.filter_text:
            return super(CodeDelegate, self).paint(painter, option, index)
        self.paint_base(painter, option, index)
        self.paint_each_letter(painter, option, index)
        return

    def paint_base(self, painter, option, index):
        #  - selected state, hover, base colour, etc
        try:
            widget = option.widget
            style = widget.style()
            Option = QStyleOptionViewItem
        except AttributeError:
            # PySide
            Option = QStyleOptionViewItemV4
            widget = None
            style = QApplication.style()

        painter.save()
        opt = Option(option)
        self.initStyleOption(opt, index)

        style.drawPrimitive(QStyle.PE_PanelItemViewItem, opt, painter, widget)

        # from https:#code.woboq.org/qt5/qtbase/src/widgets/itemviews/qstyleditemdelegate.cpp.html
        # style.drawControl(QStyle.CE_ItemViewItem, opt, painter, widget) # this draws the whole item including text. unnecessary
        painter.restore()

    # def paint_commonstyle_viewitem(self, style, opt, p, widget):
        # vopt = QStyleOptionViewItem(opt)
        # p.save()
        # p.setClipRect(opt.rect)
        # style.proxy()
        # checkRect = style.proxy().subElementRect(QStyle.SE_ItemViewItemCheckIndicator, vopt, widget)
        # iconRect = style.proxy().subElementRect(QStyle.SE_ItemViewItemDecoration, vopt, widget)
        # textRect = style.proxy().subElementRect(QStyle.SE_ItemViewItemText, vopt, widget)

        ## draw the background
        # style.proxy().drawPrimitive(QStyle.PE_PanelItemViewItem, opt, p, widget)
        ## draw the check mark
        # if (vopt.features & QStyleOptionViewItem.HasCheckIndicator):
            # option = QStyleOptionViewItem(vopt)
            # option.rect = checkRect
            # option.state = option.state & ~QStyle.State_HasFocus

            # if vopt.checkState == Qt.Unchecked:
                # option.state |= QStyle.State_Off
            # elif vopt.checkState == Qt.PartiallyChecked:
                # option.state |= QStyle.State_NoChange
            # elif vopt.checkState == Qt.Checked:
                # option.state |= QStyle.State_On

            # style.proxy().drawPrimitive(QStyle.PE_IndicatorItemViewItemCheck, option, p, widget)

            ## draw the icon
            # mode = QIcon.Normal
            # if not (vopt.state & QStyle.State_Enabled):
                # mode = QIcon.Disabled
            # elif (vopt.state & QStyle.State_Selected):
                # mode = QIcon.Selected
            # state = QIcon.On if vopt.state & QStyle.State_Open else QIcon.Off
            # vopt.icon.paint(p, iconRect, vopt.decorationAlignment, mode, state)

            ## draw the text
            # if not vopt.text.isEmpty():
                # cg = QPalette.Normal if (vopt.state & QStyle.State_Enabled) else QPalette.Disabled
                # if (cg == QPalette.Normal) and (not (vopt.state & QStyle.State_Active)):
                    # cg = QPalette.Inactive
                # if vopt.state & QStyle.State_Selected:
                    # p.setPen(vopt.palette.color(cg, QPalette.HighlightedText))
                # else:
                    # p.setPen(vopt.palette.color(cg, QPalette.Text))

                # if vopt.state & QStyle.State_Editing:
                    # p.setPen(vopt.palette.color(cg, QPalette.Text))
                    # p.drawRect(textRect.adjusted(0, 0, -1, -1))
                # self.viewItemDrawText(p, vopt, textRect) # TODO: implement https://code.woboq.org/qt5/qtbase/src/widgets/styles/qcommonstyle.cpp.html#1016

            ## draw the focus rect
             # if vopt.state & QStyle.State_HasFocus:
                # o = QStyleOptionFocusRect() # FIXME: this doesn't exist in python
                # o.QStyleOption.operator = vopt
                # o.rect = style.proxy().subElementRect(SE_ItemViewItemFocusRect, vopt, widget)
                # o.state |= QStyle.State_KeyboardFocusChange
                # o.state |= QStyle.State_Item
                # cg = QPalette.Normal if (vopt.state & QStyle.State_Enabled) else QPalette.Disabled
                # color_role = QPalette.Highlight if (vopt.state & QStyle.State_Selected) else QPalette.Window
                # o.backgroundColor = vopt.palette.color(cg, color_role)
                # style.proxy().drawPrimitive(QStyle.PE_FrameFocusRect, o, p, widget)

        # p.restore()

    def paint_each_letter(self, painter, option, index):

        painter.save()
        pattern = list(set(self.filter_text))
        text = index.data()

        font = painter.font()
        rect = QRect(option.rect)

        # little adjustments needed to match normal text placement - because of padding, I think?? maybe
        rect.moveRight(rect.right()+3)
        rect.moveTop(rect.top()+3)

        prev_found = False
        for letter in text:

            found = letter.lower() in pattern
            same_as_prev = found is prev_found
            prev_found = found
            if not same_as_prev:
                if found:
                    pen = QPen(QBrush(Qt.white), 2)
                else:
                    pen = QPen(option.palette.text(), 1)
                painter.setPen(pen)
                font.setBold(found)
                painter.setFont(font)

            painter.drawText(rect, letter)

            letter_width = QFontMetrics(font).size(Qt.TextSingleLine, letter).width()
            rect.adjust(letter_width, 0, 0, 0)
        painter.restore()

    def draw_rich_text(self, painter, option, index):
        html = index.data()
        td = QTextDocument()
        textOption = QTextOption()
        textOption.setAlignment(Qt.AlignJustify)
        textOption.setWrapMode(QTextOption.WordWrap)
        td.setDefaultTextOption(textOption)
        td.setHtml(html)
        # td.setHtml("K<sub>max</sub>=K<sub>2</sub> &middot; 3")
        painter.setFont(option.font)
        painter.translate(option.rect.topLeft())
        td.drawContents(painter)

    def set_filter_text(self, text):
        self.filter_text = text.lower()


class Tree(QTreeView):
    def __init__(self, parent=None):
        super(Tree, self).__init__(parent=parent)
        self.setFocusPolicy(Qt.ClickFocus)
        self.setHeaderHidden(True)
        self.setSelectionBehavior(QTreeView.SelectionBehavior.SelectRows)
        self.setItemDelegate(CodeDelegate(self))
        # self.setAutoExpandDelay(0)
        self.set_highlight_color()

    def set_highlight_color(self):
        palette = self.palette()
        brush = palette.highlight()
        color = brush.color()
        color.setAlphaF(0.5)
        brush.setColor(color)
        palette.setBrush(QPalette.Highlight, brush)
        self.setPalette(palette)

    @Slot(str)
    def select_first_index(self, _):
        self.select_index(self.model().index(0,0))

    @Slot(int)
    def select_row(self, row):
        self.select_index(self.model().index(row, 0))

    def select_index(self, index):
        smodel = self.selectionModel()
        smodel.setCurrentIndex(index, QItemSelectionModel.ClearAndSelect)
        self.scrollTo(index)

    @Slot(str)
    def set_filter_text(self, text):
        self.itemDelegate().set_filter_text(text)
        self.viewport().update()


class CloseIconPainter(QIconEngine):
    def pixmap(self, size, mode, state):
        img = QImage(size, QImage.Format_ARGB32)
        img.fill(QColor(0,0,0,0))
        pix = QPixmap.fromImage(img, Qt.NoFormatConversion)
        painter = QPainter(pix)
        rect = QRect(QPoint(0.0,0.0), size)
        self.paint(painter, rect, mode, state)
        return pix

    def paint(self, painter, rect, mode=QIcon.Mode.Normal, state=QIcon.State.Off):
        h = rect.height()/2
        close_rect = QRect(0,0,h,h)
        close_rect.moveCenter(rect.center())

        left_line = QLine(close_rect.topLeft(), close_rect.bottomRight())
        right_line = QLine(close_rect.topRight(), close_rect.bottomLeft())

        painter.setRenderHint(QPainter.RenderHint.HighQualityAntialiasing)

        if mode == QIcon.Disabled:
            # paint me a sunken X
            brush = QBrush(QColor.fromRgbF(1,0.2,0.2,1))
            painter.setBrush(brush)

            h = rect.height()/2
            circle_rect = QRect(0,0,h,h)
            circle_rect.moveCenter(rect.center())

            # paint me a filled circle o
            # for the "not saved"/"document modified" state
            paint_x = False
            path = QPainterPath()
            path.addEllipse(circle_rect)
            painter.fillPath(path, QBrush(QColor.fromRgbF(1,1,1,0.25)))
            return
        elif mode == QIcon.Normal:
            brush = QPalette().text()
            pen = QPen(brush, 2.4)
            painter.setPen(pen)
        elif mode == QIcon.Active:
            # paint me a bright thick X (maybe with a light square or circle underneath?) :)
            # painter.fillRect(rect.adjusted(-4,-4,2,2), QColor.fromRgbF(1,1,1,0.12))
            # h = rect.height()*2
            # x_rect = QRect(0,0,h,h)
            # x_rect.moveCenter(rect.center())
            # painter.fillRect(x_rect, QColor.fromRgbF(1,1,1,0.12))

            brush = QPalette().light()
            pen = QPen(brush, 2)
            painter.setPen(pen)
            rect.moveCenter(rect.center()+QPoint(0.5,0.5))

        # paint me a normal X
        painter.drawLine(left_line)
        painter.drawLine(right_line)


class CloseIcon(QIcon):
    def __init__(self):
        icon_painter = CloseIconPainter()
        super(CloseIcon, self).__init__(icon_painter)


class Line(QLineEdit):
    close_signal = Signal()
    def __init__(self, parent=None):
        super(Line, self).__init__(parent=parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setTextMargins(5,2,5,2)
        self.setMouseTracking(True)
        try:
            self.add_close_action()
        except TypeError:
            # not worth supporting on PySide
            pass

    def eventFilter(self, obj, event):
        if obj == self.btn:
            # trick the QToolButton into having a Hover state by hijacking the Disabled state.
            if event.type() == QEvent.Enter:
                # self.btn.setDown(True)
                self.btn.setEnabled(True)
            if event.type() == QEvent.Leave:
                # self.btn.setDown(False)
                self.btn.setEnabled(False)
        return False

    def closeEvent(self, event):
        super(Line, self).closeEvent(event)
        self.btn.removeEventFilter(self)

    def add_close_action(self):
        self.close_action = QAction()
        icon = CloseIcon()
        self.close_action.setIcon(icon)
        self.close_action.setCheckable(True)
        self.addAction(self.close_action, QLineEdit.TrailingPosition)
        self.close_action.triggered.connect(self.close_signal.emit)

        self.btn = self.children()[1]
        self.btn.setEnabled(False)
        self.btn.installEventFilter(self)

    def set_text_from_index(self, selected, deselected):
        for index in selected.indexes():
            text = index.data()
            self.setPlaceholderText(text.strip())
            break


class PopupLine(Popup):
    def __init__(self, editor):
        super(PopupLine, self).__init__(parent=editor)

        self.editor = editor
        self.current_scroll = editor.verticalScrollBar().value()
        self.line_edit = Line()
        self.line_edit.setFont(editor.font())
        self.tree_view = Tree()
        self.tree_view.setFont(editor.font())

        self.setFocusProxy(self.line_edit)
        self.tree_view.setFocusProxy(self.line_edit)

        self.editor.installEventFilter(self)
        self.line_edit.installEventFilter(self)
        self.tree_view.installEventFilter(self)

        self.symbol_model = SymbolModel()
        self.proxy_model = ProxyModel()
        self.proxy_model.setSourceModel(self.symbol_model)
        self.tree_view.setModel(self.proxy_model)
        # TODO: set tree_view current selection to the first symbol above the current line using LINENO_ROLE

        self.setLayout(QVBoxLayout(self))
        layout = self.layout()
        layout.addWidget(self.line_edit)
        layout.addWidget(self.tree_view)

        # signals
        self.line_edit.editingFinished.connect(self.close)
        self.line_edit.close_signal.connect(self.close)
        self.line_edit.textChanged.connect(self.proxy_model.setFilterRegExp)
        self.line_edit.textChanged.connect(self.tree_view.set_filter_text)
        self.line_edit.textChanged.connect(self.tree_view.select_first_index, Qt.QueuedConnection)
        self.symbol_model.loading_complete.connect(self.tree_view.select_row)
        # delay this connection so we don't jump straight to the first
        QTimer.singleShot(10, self.connect_goto_signal)

        # fill with data
        self.symbol_model.populate_from_editor(editor)

    def connect_goto_signal(self):
        smodel = self.tree_view.selectionModel()
        smodel.selectionChanged.connect(self.line_edit.set_text_from_index)
        smodel.selectionChanged.connect(self.goto_line)

        # if we have a selection, use it
        self.line_edit.setText(self.editor.selected_text())
        self.line_edit.selectAll()

    def showEvent(self, event):
        super(PopupLine, self).showEvent(event)
        self.line_edit.setFocus(Qt.TabFocusReason)

    def closeEvent(self, event):
        self.editor.removeEventFilter(self)
        self.line_edit.removeEventFilter(self)
        self.tree_view.removeEventFilter(self)
        self.editor.setFocus(Qt.MouseFocusReason)
        super(PopupLine, self).closeEvent(event)

    def eventFilter(self, obj, event):
        if obj == self.editor:
            if event.type() == QEvent.Move:
                self.place_over_parent()
            elif event.type() == QEvent.Resize:
                self.place_over_parent()
            elif event.type() in [QEvent.Hide, QEvent.Close, QEvent.FocusIn]:
                self.close()
        elif obj == self.tree_view:
            if event.type() == QEvent.FocusIn:
                self.line_edit.setFocus(Qt.TabFocusReason)
            # elif event.type() == QEvent.MouseButtonPress: # TODO: click on item to close it? maybe
                # self.close()

        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Escape:
                self.cancel()
                return True
            elif event.key() in [Qt.Key_Return, Qt.Key_Enter]: # TODO: Qt.Key_Left and right if we go with an expandable tree structure
                self.close()
                return True
            elif event.key() in [Qt.Key_Up, Qt.Key_Down, Qt.Key_PageUp, Qt.Key_PageDown, Qt.Key_Tab]:
                if obj in [self.line_edit, self.editor]:
                    self.tree_view.keyPressEvent(event)
                    return True
        return False

    def goto_line(self, selected, deselected):
        for index in selected.indexes():
            lineno = index.data(LINENO_ROLE)
            goto_line(self.editor, lineno, scroll=True)
            break

    def cancel(self):
        self.close()

        # restore everything to how it was
        goto_line(self.editor, self.symbol_model.current_lineno, scroll=False)
        self.editor.verticalScrollBar().setValue(self.current_scroll)



if __name__ == '__main__':

    # test
    popup = PopupLine(_ide.python_editor.editor)
    popup.show()
    self = popup
    # popup.tree_view.close()
    # popup.close()
