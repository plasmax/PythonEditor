from Qt import QtGui, QtCore, QtWidgets

class LineNumberArea(QtWidgets.QWidget):

    def __init__(self, editor):
        super(LineNumberArea, self).__init__(editor)
        self.editor = editor
        self.setupLineNumbers()

    def sizeHint(self):
        return QtCore.QSize(self.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        mypainter = QtGui.QPainter(self)

        block = self.editor.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top()
        bottom = top + self.editor.blockBoundingRect(block).height()

        height = self.editor.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(blockNumber + 1)
                mypainter.setPen(QtCore.Qt.darkGray)
                mypainter.drawText(0, top, self.width(), height,
                 QtCore.Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.editor.blockBoundingRect(block).height()
            blockNumber += 1

    def setupLineNumbers(self):
        self.editor.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.editor.updateRequest.connect(self.updateLineNumberArea)
        self.editor.updateRequest.connect(self.resizeLineNo)
        self.editor.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateLineNumberAreaWidth(0)

    def lineNumberAreaWidth(self):
        digits = 1
        count = max(1, self.editor.blockCount())
        while count >= 10:
            count /= 10
            digits += 1
        space = 3 + self.editor.fontMetrics().width('9') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.editor.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.editor.scroll(0, dy)
        else:
            self.editor.update(0, rect.y(), self.editor.width(),
                       rect.height())

        if rect.contains(self.editor.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def highlightCurrentLine(self):
        extraSelections = []

        if not self.editor.isReadOnly():
            selection = QtWidgets.QTextEdit.ExtraSelection()

            lineColor = self.editor.palette().color(QtGui.QPalette.Background).darker(100)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
            selection.cursor = self.editor.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.editor.setExtraSelections(extraSelections)
        
    def resizeLineNo(self):

        cr = self.editor.contentsRect();
        self.setGeometry(QtCore.QRect(cr.left(), cr.top(),
                    self.lineNumberAreaWidth(), cr.height()))