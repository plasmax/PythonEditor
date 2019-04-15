from Qt import QtWidgets, QtGui, QtCore

class PopupBarTest(QtCore.QObject):
    """
    Test class for the popup_bar    
    """
    show_popup_signal = QtCore.Signal()
    def __init__(self, tabs):
        super(PopupBarTest, self).__init__()
        #self.setParent(tabs)
        
        self.tabeditor = tabs
        self.editor = tabs.editor
        self.tabs = tabs.tabs
        self.setParent(tabs)
        self.show_popup_signal.connect(self.show_popup_bar)
        
    def show_popup_bar(self):
        #editor = _ide.python_editor.editor
        #layout = _ide.python_editor.tabeditor.layout()
        
        editor = self.editor
        layout = self.tabeditor.layout()

        # first remove any previous widgets
        name = 'Document out of sync warning'
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item is None:
                continue
            widget = item.widget()
            if widget.objectName() != name:
                continue
            layout.removeItem(item)
            widget.deleteLater()

        popup_bar = QtWidgets.QWidget()
        popup_bar.setObjectName('Document out of sync warning')
        bar_layout = QtWidgets.QHBoxLayout(popup_bar)

        l = QtWidgets.QLabel()
        l.setText('This tab is out of sync with the autosave.')
        new_button     = QtWidgets.QPushButton('Load into New Tab')
        save_button    = QtWidgets.QPushButton('Save This Version')
        update_button  = QtWidgets.QPushButton('Update From Autosave')
        diff_button    = QtWidgets.QPushButton('Show Diff')

        stylesheet = """
        QPushButton { background-color: #444; }
        QPushButton:hover { background-color: orange; }
        """

        for b in new_button, save_button, update_button, diff_button:
            #b.setFlat(True)
            b.setStyleSheet(stylesheet)

        for b in l, new_button, save_button, update_button, diff_button:
            bar_layout.addWidget(b)

        layout.insertWidget(1, popup_bar)
        popup_bar.setMaximumHeight(0)

        #print popup_bar.maximumHeight()
        #popup_bar.setMaximumHeight(46)
        def anim_popup_bar(popup_bar):
            anim = QtCore.QPropertyAnimation(
                popup_bar, 
                'maximumHeight'
            )
            anim.setStartValue(0)
            anim.setEndValue(46)
            anim.setDuration(400)
            anim.start()
            anim_popup_bar.anim = anim

        anim_popup_bar(popup_bar)
    
tabs = _ide.python_editor.tabeditor
def test_A():
    A = PopupBarTest(tabs)
    for i in range(1):
        A.show_popup_signal.emit()
        #A.show_popup_bar()
    
#test_A()
QtCore.QTimer.singleShot(300, test_A)
#&&

anim2 = QtCore.QPropertyAnimation(popup_bar, 'maximumHeight')
#anim2.setStartValue(popup_bar.maximumHeight())
anim2.setStartValue(46)
anim2.setEndValue(0)
anim2.setDuration(500)
from functools import partial
start = partial(QtCore.QTimer.singleShot, 1200, anim2.start)
anim.finished.connect(start)

#anim2.finished.connect(popup_bar.deleteLater)

#&&

anim = QtCore.QPropertyAnimation(popup_bar, 'size')
anim.setStartValue(QtCore.QSize(958, 0))
anim.setEndValue(QtCore.QSize(958, 46))
anim.setDuration(300)
anim.start()

#&&
item.geometry()
item.setGeometry(QtCore.QRect(0,0,958,0))
layout.setSpacing(0)
#layout.setSizeConstraint(layout.SetFixedSize)
layout.setSizeConstraint(layout.SetNoConstraint)
layout.setSizeConstraint(layout.SetDefaultConstraint)
#&&
anim = QtCore.QPropertyAnimation(popup_bar, 'height')
anim.setStartValue(0)
anim.setEndValue(246)
anim.setDuration(500)
anim.start()


#&&
anim = QtCore.QPropertyAnimation(popup_bar, 'geometry')
x,y,w,h = editor.rect().getRect()
start_rect = QtCore.QRect(x, y, w, 70)
anim.setStartValue(start_rect)
end_rect = QtCore.QRect(x, y, w, 110)
anim.setEndValue(end_rect)
anim.setDuration(1500)
anim.start()



#def add_items():
#anim.finished.connect(add_items)
#&&
#editor.resize(editor.width(), editor.height()-40)
#editor.move(editor.x(), editor.y()+40)
    
w.show()
w.raise_()
#&&
wg = [a for a in editor.children() if isinstance(a, QtWidgets.QWidget)]