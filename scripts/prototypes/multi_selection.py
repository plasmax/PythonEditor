from Qt.QtGui import *
from Qt.QtCore import *
from Qt.QtWidgets import *
from PythonEditor.ui import editor


#class MultiCursor(editor.Editor):
class MultiCursor(QPlainTextEdit):
    def paintEvent(self, event):
        super(MultiCursor, self).paintEvent(event)
        painter = QPainter(self.viewport())
        offset = self.contentOffset()
        '''
        pen = QPen(Qt.yellow, 12, Qt.SolidLine)
        painter.setPen(pen)
        '''
        for c in self.cursors():
          block = c.block()
          l = block.layout()
          l.drawCursor(
            painter,
            offset, # QPointF
            c.position(),# int
            2 # width:int
          )

    def mousePressEvent(self, event):
        app = QApplication
        mods = app.keyboardModifiers()
        if mods == Qt.ControlModifier:
          self.add_cursor(
            self.cursorForPosition(
              event.pos()
            )
          )
        return super(
          MultiCursor, self
        ).mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self._cursors=[]
            self.repaint()
        elif (
          event.key() in [
            Qt.Key_Up,
            Qt.Key_Down
          ]
          and event.modifiers() == Qt.ControlModifier|Qt.AltModifier
          ):
            self._cursors.append(
              self.textCursor()
            )

        return super(
            MultiCursor, self
        ).keyPressEvent(event)

    _cursors = []
    def cursors(self):
        """
        List of QTextCursors used to make
        multi-edits.
        """
        return self._cursors

    def add_cursor(self, cursor):
        self._cursors.append(
          cursor
        )

    def keyPressMulti(self, event):
        multi_keys = [
          Qt.Key_Up,
          Qt.Key_Down,
          Qt.Key_Left,
          Qt.Key_Right,
        ]
        k = event.key()
        if k not in multi_keys:
          return
        for c in self.cursors():
           c # insert key


m = MultiCursor()
m.show()
m.setPlainText("""
some boring test text
some boring test text
some boring test text
some boring test text

some boring test text
""")
