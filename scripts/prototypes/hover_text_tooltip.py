import os
import re
from Qt import QtWidgets, QtGui, QtCore

PHC = QtCore.Qt.PointingHandCursor
ARC = QtCore.Qt.ArrowCursor

LUC = QtGui.QTextCursor.LineUnderCursor
WUC = QtGui.QTextCursor.WordUnderCursor
BUC = QtGui.QTextCursor.BlockUnderCursor
class HoverText(QtWidgets.QPlainTextEdit):
    hovered_word = ''
    def __init__(self):
        super(HoverText, self).__init__()
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        super(HoverText, self).mousePressEvent(event)
        if self._cur_path:
            print self._cur_path
        
    def enterEvent(self, event):
        self.mouse_in = True
        print 'in'
        super(HoverText, self).enterEvent(event)
    
    def leaveEvent(self, event):
        self.mouse_in = False
        print 'out'
        super(HoverText, self).leaveEvent(event)

    def mouseMoveEvent(self, event):
        super(HoverText, self).mouseMoveEvent(event)
        if not self.mouse_in:
            return

        pos = event.pos()
        tc = self.cursorForPosition(pos)
        tc.select(BUC)
        sel = tc.selection()
        text = sel.toPlainText().strip()
        #if not text:
            #return
        same = (self.hovered_word == text)
        if not same:
            self.hovered_word = text
            #return
        #c = QtGui.QCursor()
        #c = self.cursor()

        #self.cursor()
        #self.cursor().setShape(ARC)
        #self.cursor().setShape(PHC)
        #c.setShape(PHC)
        ptn = '(?<=\")([^\"]+)(?=\")'
        pbc = re.findall(ptn, text)
        
        app = QtWidgets.QApplication
        
            
        pos = event.pos()
        tc = self.cursorForPosition(pos)
        tc.select(WUC)
        sel = tc.selection()
        word = sel.toPlainText().strip()
        
        if pbc:
            self._cur_path = pbc[0]
        else:
            self._cur_path = ''
        
        if not os.path.isfile(self._cur_path):
            self._cur_path = ''
            
        if word and word in self._cur_path:
            app.setOverrideCursor(PHC)
        else:
            app.restoreOverrideCursor()
        app.processEvents()
            #print text
    #else:
        #c.setShape(ARC)
    #self.setCursor(c)
        
ht = HoverText()
ht.show()

text = r"""
Python 2.7.9 (default, Dec 10 2014, 12:28:03) [MSC v.1500 64 bit (AMD64)]
on win32
Type "copyright", "credits" or "license()" for more information.
>>> ================================ RESTART ================================
Enter salesperson ID or 9999 to quit: 1584
Traceback (most recent call last):
File "C:\Repositories\PythonEditor\PythonEditor\ui\features\autocompletion.py",
line 8, in <module>
while salesPersonID != 9999:
NameError: name 'salesPersonID' is not defined
"""
ht.setPlainText(text)

QtGui.QCursor().shape()
QtGui.QCursor().setShape(PHC)
#QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.PointingHandCursor)
#QtWidgets.QApplication.restoreOverrideCursor()

os.path.isdir('C:')


cursors = [c for c in dir(QtCore.Qt) if 'cursor' in c.lower()]
for l in """
['ArrowCursor', 'BitmapCursor', 'BlankCursor', 'BusyCursor', 'ClosedHandCursor', 'CrossCursor', 'CursorMoveStyle', 'CursorShape', 'CustomCursor', 'DragCopyCursor', 'DragLinkCursor', 'DragMoveCursor', 'ForbiddenCursor', 'IBeamCursor', 'ImCursorPosition', 'LastCursor', 'NavigationModeCursorAuto', 'NavigationModeCursorForceVisible', 'OpenHandCursor', 'PointingHandCursor', 'SizeAllCursor', 'SizeBDiagCursor', 'SizeFDiagCursor', 'SizeHorCursor', 'SizeVerCursor', 'SplitHCursor', 'SplitVCursor', 'UpArrowCursor', 'WA_SetCursor', 'WaitCursor', 'WhatsThisCursor']""".split():
    #print l
    pass
    
['ArrowCursor',
'BitmapCursor',
'BlankCursor',
'BusyCursor',
'ClosedHandCursor',
'CrossCursor',
'CursorMoveStyle',
'CursorShape',
'CustomCursor',
'DragCopyCursor',
'DragLinkCursor',
'DragMoveCursor',
'ForbiddenCursor',
'IBeamCursor',
'ImCursorPosition',
'LastCursor',
'NavigationModeCursorAuto',
'NavigationModeCursorForceVisible',
'OpenHandCursor',
'PointingHandCursor',
'SizeAllCursor',
'SizeBDiagCursor',
'SizeFDiagCursor',
'SizeHorCursor',
'SizeVerCursor',
'SplitHCursor',
'SplitVCursor',
'UpArrowCursor',
'WA_SetCursor',
'WaitCursor',
'WhatsThisCursor']
