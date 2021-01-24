# cleaner tabbar implementation for pythoneditor
"""
TODO:
[x] Close button - permanent on selected tab, available over hovered tab
[x] Line edit for editing tab name
[x] Tab width/height controlled without stylesheets
[x] Tab tooltips with setTabToolTip()
[x] Line edit should quit on esc and focus out
[ ] Get rid of the <> buttons
[ ] Offset tab text a little to the left (probably need to paint it)
[ ] Draw close button when tab is moving
[ ] use QDataWidgetMapper to map tabs to XML data
[ ] hide RHS buttons, add custom ones
[ ] middle click to close tab
"""
try:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
    from PySide2.QtGui import *
except ImportError:
    from PySide.QtCore import *
    from PySide.QtGui import *


class NameEdit(QLineEdit):
    def __init__(self, parent=None):
        super(NameEdit, self).__init__(parent=parent)
        self.setTextMargins(3,1,3,1)
        self.setWindowFlags(Qt.FramelessWindowHint)
    
    def keyPressEvent(self, event):
        QLineEdit.keyPressEvent(self, event)
        if event.key()==Qt.Key_Escape:
            self.hide()


class Tabs(QTabBar):
    def __init__(self):
        super(Tabs, self).__init__()
        self.hovered_index = -1
        self.close_button_hovered = -1
        self.close_button_pressed = -1
        
        self.setSelectionBehaviorOnRemove(QTabBar.SelectPreviousTab)
        self.setMovable(True)
        self.setMouseTracking(True)
        
        self.line_edit = NameEdit(self)
        self.line_edit.editingFinished.connect(self.name_edited)
        self.line_edit.hide()
        
        # self.currentChanged.connect(self.set_current)
        
    # def tabRemoved(self, index):
        # QTabBar.tabRemoved(self, index)
    
    # def tabRect(self, index):
        # rect = QTabBar.tabRect(self, index)
        ## print 'rect', rect
        # rect.adjust(0,0,0,0)
        # return rect
        
    def tabSizeHint(self, index):
        size = QTabBar.tabSizeHint(self, index)
        size.setWidth(size.width()+50)
        size.setHeight(size.height()+6)
        return size
        
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            index = self.tabAt(event.pos())
            rect = self.get_close_button_rect(index)
            if not rect.contains(event.pos()):
                self.show_line_edit(index)
        else:
            QTabBar.mouseDoubleClickEvent(self, event)
            
    def mousePressEvent(self, event):
        if event.button()==Qt.LeftButton:
            self.line_edit.hide()
            
            index = self.tabAt(event.pos())
            rect = self.get_close_button_rect(index)
            if rect.contains(event.pos()):
                self.close_button_pressed = index
                self.update()
                return
        QTabBar.mousePressEvent(self, event)
            
    def mouseReleaseEvent(self, event):
        if event.button()==Qt.LeftButton:
            index = self.tabAt(event.pos())
            rect = self.get_close_button_rect(index)
            if rect.contains(event.pos()):
                self.close_button_pressed = -1
                self.update()
                self.removeTab(index)
                return
        QTabBar.mouseReleaseEvent(self, event)

    def mouseMoveEvent(self, event):
        QTabBar.mouseMoveEvent(self, event)
                    
        index = self.tabAt(event.pos())
        if index != self.hovered_index:
            self.hovered_index = index
            
        index = self.tabAt(event.pos())
        rect = self.get_close_button_rect(index)
        if rect.contains(event.pos()):
            self.close_button_hovered = index
        else:
            self.close_button_hovered = -1

        self.update()
        
    def paintEvent(self, event):
        QTabBar.paintEvent(self, event)
        
        """ # TODO: First step - draw the text! then tab controls
        painter = QPainter(self)
        painter.save()
        for i in range(self.count()):
            rect = self.tabRect(i)
            if event.rect().contains(rect):
                text = self.tabText(i)
                painter.drawText(rect.bottomLeft(), text)
        painter.restore()
        """

        index = self.currentIndex()
        self.draw_close_button(index)
        if self.hovered_index not in [index, -1]:
            self.draw_close_button(self.hovered_index)        
            
    def draw_close_button(self, index):
        painter = QPainter(self)
        painter.save()

        opt = QStyleOption()
        opt.initFrom(self)
        opt.rect = self.get_close_button_rect(index)
        if self.close_button_pressed == index:
            opt.state |= QStyle.State_Sunken
        elif self.close_button_hovered == index:
            opt.state |= QStyle.State_Raised
        else:
            opt.state = QStyle.State_Enabled
        
        self.style().drawPrimitive(
            QStyle.PE_IndicatorTabClose,
            opt,
            painter,
            self
        )
        painter.restore()
        
    # def set_current(self, index):
        # print index
        
    def get_close_button_rect(self, index):
        rect = self.tabRect(index)
        size = self.tabSizeHint(index)
        h = size.height()/2
        return QRect(-25, h-8, 16, 16).translated(rect.topRight())
        
    def show_line_edit(self, index):
        self.line_edit.current_index = index
        rect = self.tabRect(index)
        self.line_edit.setGeometry(rect)
        text = self.tabText(index)
        self.line_edit.setText(text)
        self.line_edit.show()
        self.line_edit.selectAll()
        self.line_edit.setFocus(Qt.MouseFocusReason)
    
    def name_edited(self):
        self.setTabText(self.line_edit.current_index, self.line_edit.text())
        self.line_edit.hide()



tab = Tabs()
self = tab # for dev purposes
for i in range(20):
    tab.addTab('test %i'%i)
    tab.setTabToolTip(i, 'test %i'%i)

w = QWidget()
w.setLayout(QVBoxLayout(w))
w.layout().addWidget(tab)
w.show()