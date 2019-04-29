from Qt.QtGui import *
from Qt.QtCore import *
from Qt.QtWidgets import *
from PythonEditor.ui import editor

#class MultiCursor(editor.Editor):
class MultiCursor(QPlainTextEdit):
    def paintEvent(self, event):
        super(MultiCursor, self).paintEvent(event)
        painter = QPainter(self.viewport())
        
        '''
        pen = QPen(Qt.yellow, 12, Qt.SolidLine)
        painter.setPen(pen)
        '''
        for c in self.cursors():
          block = c.block()
          l = block.layout()
          position=c.position()
          width=2
          l.drawCursor(
            painter,
            position, #QPointF
            cursorPosition,#int
            width#int
            )

            cp = c.position()
            doc = self.document()
    
    def mousePressEvent(self, event):
        mods = QApplication.keyboardModifiers()
        if mods == Qt.ControlModifier:
          self.insert_cursor(
            self.cursorForPosition(
              event.pos()
            )
          )
          '''
            selections = self.extraSelections()
            pos = event.pos()
            cursor = self.cursorForPosition(pos)
            cursor.select(cursor.WordUnderCursor)
            sel = QTextEdit.ExtraSelection()
            sel.cursor = cursor
            colour = QtGui.QColor(191, 191, 191, 189)
            sel.format.setBackground(colour)
            sel.__multicursor = True
            setattr(sel, '__multicursor', True)
            selections.append(sel)
            self.setExtraSelections(selections)
          '''
        return super(MultiCursor, self).mousePressEvent(event)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self._cursors=[]
        return super(MultiCursor, self).keyPressEvent(event)

    _cursors = []
    def cursors(self):
        """
        List of QTextCursors used to make
        multi-edits.
        """
        return self._cursors

    def insert_cursor(self,cursor):
      # sort cursors by position
      # use new cursor position to
      # figure out which index to 
      # insert cursor in
        self._cursors.insert(
          index,
          cursor
        )
    
        
m = MultiCursor()
m.show()
m.setPlainText("""
some boring test text
some boring test text
some boring test text
some boring test text

some boring test text
""")
