"""
A nice solution using a single editor and 
a subclassed QTabBar with 

need my new tab button!!!!

update the tab dict['text'] on every keypress
then pick it up smoothly with a background thread
reading the dict data
"""

from Qt import QtWidgets, QtGui, QtCore
from PythonEditor.ui.features import autosavexml
import time

start = time.time()

""" a nice idea but not sure if i need it yet
class Tab(object):
    uid = None
    name = None
    text = ''
    path = ''
    date = ''
    def __setitem__(self, name, value):
        setattr(self, name, value)
    
    def __getitem__(self, name):
        return getattr(self, name)
    
    def __repr__(self):
        s = '<Tab>'
        for 
        s += 
"""        
    

class Tabs(QtWidgets.QTabBar):
    pen = QtGui.QPen()
    brush = QtGui.QBrush()
    mouse_over_rect = False
    over_button = -1

    def __getitem__(self, index):
        if isinstance(index, int):
            return self.tabData(index)
        elif isinstance(index, str):
            i = self.currentIndex()
            return self.tabData(i)[index]
        
    def __setitem__(self, index, data):
        if isinstance(index, int):
            return self.setTabData(index, data)
        elif isinstance(index, str):
            i = self.currentIndex()
            tab_data = self.tabData(i)
            tab_data[index] = data
            return self.setTabData(i, tab_data)
        
    def tab_close_button_rect(self, i):
        rect = self.tabRect(i)
        rqt = QtCore.QRect(rect)
        w = rect.right()-rect.left()
        o = 5
        rqt.adjust(w-25+o, 5, -15+o, -5)
        return rqt
        
    def event(self, e):
        """
        Trigger button highlighting if 
        hovering over (x) close buttons
        """
        if e.type() == QtCore.QEvent.Type.HoverMove: # does the cover tablet?
            pt = e.pos()
            for i in range(self.count()):
                rect = self.tabRect(i)
                
                if not self.rect().contains(rect):
                    continue # would be nice to optimise

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
        return super(Tabs, self).event(e)
        
    def paint_close_button(self):
        """
        Let's draw a tiny little x on the right
        that's our new close button. It's just two little lines! x
        
        Notes: 
        - it's probably faster if we only iterate over visible tabs.
        - How can this be used to write italic text? 
        - we could change the x to a o like sublime
        - ANTIALIASING PLEASEEEEEEEEEEEEEEEEEEEEEEEEEEEEE
        """
        #print 1
        #print dir(e)
        #e.accept()
        #paint_rect = e.rect()

        for i in range(self.count()):
            rect = self.tabRect(i)
            
            if not self.rect().contains(rect):
                continue # would be nice to optimise

            #if rect == paint_rect:
                #print rect
            #print 'tab:    ', rect
            x,y,r,t = rect.getCoords()
            #print rect.getCoords()
            #rqt = QtCore.QRect(x+(r/2),y,r+1,t+1)
            rqt = self.tab_close_button_rect(i)
            #QtCore.QRect.right()
            
            #QtCore.QRect.adjust()
            #print 'rt side:', rqt
            #print e.region()
            p = QtGui.QPainter()
            #p.setRenderHint(QtGui.QPainter.Antialiasing)
            p.begin(self)
            p.setBrush(self.brush)
            if i == self.over_button:
                if self.mouse_over_rect:
                    brush = QtGui.QBrush(QtCore.Qt.gray)
                    p.setBrush(brush)
            p.setPen(None)
            p.setRenderHint(QtGui.QPainter.Antialiasing)
            #p.drawEllipse(rqt)
                    
            p.setPen(self.pen)
            self.pen.setWidth(2)
            if i == self.over_button:
                if self.mouse_over_rect:
                    pen = QtGui.QPen(QtCore.Qt.white)
                    pen.setWidth(2)
                    p.setPen(pen)

                    #p.save()

            #print rect
            #for x in range(0, self.width(), 50):
                #for y in range(0, self.height(), 50):
                    #p.translate(x,y)
            #p.drawText(rect, QtCore.Qt.AlignCenter, 'tab')

            #x,y,r,t = rqt.x, rqt.y, rqt.right(), rqt.top()
            #bl = rqt.bottomLeft()
            #tr = rqt.topRight()
            #p.drawLine(bl, tr)
            
            a = 2

            rqt.adjust(a,a,-a,-a)
            p.drawLine(rqt.bottomLeft(), rqt.topRight())
            p.drawLine(rqt.topLeft(), rqt.bottomRight())
            #p.restore()
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
                        self.removeTab(i) # this should emit a close signal like the current tabwidget
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



"""
for e in dir(Tabs):
    if 'event' in e.lower():
        print e
"""


button_dict = {}
tabs = Tabs()
tabs.setMovable(True)
tabs.setDrawBase(True)
stylesheet = """
QTabBar::tab {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
    height: 24px;
    padding-right: 50px;
}
"""
stylesheet = """
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
tabs.setStyleSheet(stylesheet)
#tabs = QtWidgets.QTabBar()
#tabs.setExpanding(True)


root, subscripts = autosavexml.parsexml('subscript')

autosaves = []
i = 0
for s in subscripts:
    name = s.attrib.get('name')
    if name is None:
        continue
    autosaves.append((i, s))
    i += 1
    
for i, s in autosaves:
    name = s.attrib.get('name')
    data = s.attrib.copy()
    tabs.addTab(name+' '*5) # hax for enough space for close button :'(
    path = data.get('path')
    if path is not None:
        tabs.setTabToolTip(i, path) # and if this changes?
    data['text'] = s.text # we might need to fetch the text from a file
    tabs.setTabData(i, data)
    
"""
tab = Tab()
for key, value in data.items():
    tab[key] = value
pprint(tab.__dict__)
"""

tabs.setCurrentIndex(i)
w = QtWidgets.QWidget()
l = QtWidgets.QVBoxLayout(w)
w.setLayout(l)
l.addWidget(tabs)
s = QtWidgets.QStackedWidget()
#s.addWidget('a')
editor = PythonEditor.ui.editor.Editor()

@QtCore.Slot(int)
def set_editor_contents(index):
    data = tabs.tabData(index)
    text = data['text'] #
    editor.setPlainText(text)
    editor.name = data['name']
    editor.uid = data['uuid']
    editor.path = data.get('path')
    
def save_text_in_tab():
    if editor.uid == tabs['uuid']:
        tabs['text'] = editor.toPlainText()

current_index = tabs.currentIndex()
data = tabs.tabData(current_index)
editor.setPlainText(data['text'])
tabs.currentChanged.connect(set_editor_contents)

# this is something we're going to want only 
# when tab already set (and not when switching)
editor.textChanged.connect(save_text_in_tab) 

l.addWidget(editor)
w.show()

from pprint import pprint
#pprint(tabs[2])
tabs['text']
#sys.getsizeof(w)

duration = (time.time()-start)
print '%.3f seconds to launch %s tabs' % (duration, i)