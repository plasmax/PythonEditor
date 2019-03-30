from Qt import QtWidgets, QtGui, QtCore
from PythonEditor.ui import editor

#class MultiCursor(editor.Editor):
class MultiCursor(QtWidgets.QPlainTextEdit):
    def paintEvent(self, event):
        #super(MultiCursor, self).paintEvent(event)
        #for s in self.multiSelections():
        painter = QtGui.QPainter(self)
        pen = QtGui.QPen(QtCore.Qt.yellow, 12, QtCore.Qt.SolidLine)
        painter.setPen(pen)
        painter.begin(self)
        
        for s in self.extraSelections():
            #s = QtWidgets.QTextEdit.ExtraSelection
            c = s.cursor
            #c = QtGui.QTextCursor
            #c.position()
            cr = self.cursorRect(c)
            QtCore.QRect
            coords = cr.getCoords()
            print coords
            painter.drawLine(*coords)
            cp = c.position()
            doc = self.document()
            #QtGui.QTextDocument.draw
            #print self.getPaintContext()
            #QtGui.QAbstractTextDocumentLayout.PaintContext

            #c.select(c.WordUnderCursor)
            #QtGui.QTextLayout.drawCursor(painter, cr.center(), cp)
            #painter.drawLine
            #print c.selection().toPlainText()
        #return super(MultiCursor, self).paintEvent(event)
        painter.end()
        super(MultiCursor, self).paintEvent(event)
    
    def mousePressEvent(self, event):
        mods = QtWidgets.QApplication.keyboardModifiers()
        if mods == QtCore.Qt.ControlModifier:
            selections = self.extraSelections()
            pos = event.pos()
            cursor = self.cursorForPosition(pos)
            cursor.select(cursor.WordUnderCursor)
            sel = QtWidgets.QTextEdit.ExtraSelection()
            sel.cursor = cursor
            colour = QtGui.QColor(191, 191, 191, 189)
            sel.format.setBackground(colour)
            sel.__multicursor = True
            setattr(sel, '__multicursor', True)
            selections.append(sel)
            self.setExtraSelections(selections)
        return super(MultiCursor, self).mousePressEvent(event)
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.setExtraSelections([])
        return super(MultiCursor, self).keyPressEvent(event)

    def extraSelections(self, attr=None):
        """
        Let QPlainTextEdit.extraSelections
        allow selection type filtering.
        """
        selections = super(MultiCursor, self).extraSelections()
        if attr is None:
            return selections
        return filter(lambda x: hasattr(x, attr), selections)

    def multiSelections(self):
        return self.extraSelections(attr='__multicursor')
    
    def setExtraSelections(self, selections, attr=None):
        if attr is not None:
            selections = filter(
                lambda x: hasattr(x, attr), 
                selections
            )
        return super(MultiCursor,self).setExtraSelections(selections)
        
m = MultiCursor()
m.show()
m.setPlainText("""
some boring test text
some boring test text
some boring test text
some boring test text

some boring test text
""")
