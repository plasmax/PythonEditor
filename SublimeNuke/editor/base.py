import sys
import re
import time
print 'importing', __name__, 'at', time.asctime()

try:
    import PySide
    import nuke
except:
    sys.path.append('C:/Users/Max-Last/.nuke/python/external')

from PySide import QtGui, QtCore

from features import syntaxhighlighter
reload(syntaxhighlighter)

LEVEL_THREE = True

class CodeEditor(QtGui.QPlainTextEdit):

    def __init__(self, file, _globals={}, _locals={}):
        super(CodeEditor, self).__init__()
        self._file = file
        self._globals = _globals
        self._locals = _locals

        syntaxhighlighter.Highlight(self.document())

        if not True: #temp disable stylesheet for development
            self.setStyleSheet('background:#282828;color:#EEE;') # Main Colors
            self.font = QtGui.QFont()
            self.font.setFamily("Courier")
            self.font.setStyleHint(QtGui.QFont.Monospace)
            self.font.setFixedPitch(True)
            self.font.setPointSize(8)
            self.setFont(self.font)
            self.setTabStopWidth(4 * QtGui.QFontMetrics(self.font).width(' '))

        self.setTabStopWidth(4 * QtGui.QFontMetrics(self.font()).width(' '))

    def keyReleaseEvent(self, event):
        """
        File edit commits happen on keyRelease.
        """

        with open(self._file, 'w') as f:
            f.write(self.toPlainText())

        super(CodeEditor, self).keyReleaseEvent(event)
        
    def keyPressEvent(self, event):
        """
        What happens when keys are pressed.
        """
        if event.key() in (QtCore.Qt.Key_Return,
                           QtCore.Qt.Key_Enter):
            if event.modifiers() == QtCore.Qt.ControlModifier:
                self.begin_exec()

            elif event.modifiers() == QtCore.Qt.ShiftModifier | QtCore.Qt.ControlModifier:
                textCursor = self.textCursor()
                line = textCursor.block().text()
                indentCount = len(line) - len(line.lstrip(' '))
                textCursor.movePosition(textCursor.StartOfLine)
                self.setTextCursor(textCursor)
                textCursor.insertText(' '*indentCount+'\n')
                self.moveCursor(textCursor.Left)
                return True
            else:
                textCursor = self.textCursor()
                line = textCursor.block().text()
                indentCount = len(line) - len(line.lstrip(' '))
                textCursor.insertText('\n'+' '*indentCount)
                return True

        if event.key() == QtCore.Qt.Key_Tab:
            textCursor = self.textCursor()
            textCursor.insertText('    ')
            return True

        if (event.key() == QtCore.Qt.Key_Slash
                and event.modifiers() == QtCore.Qt.ControlModifier):
            textCursor = self.textCursor()
            text = textCursor.selection()#.toPlainText()
            print text
            raise NotImplementedError, 'add comment code toggle here'
            # block = textCursor.block()
            # print block
            # line = textCursor.block().text()
            # print line
            # textCursor.movePosition(textCursor.StartOfLine)
            # self.setTextCursor(textCursor)
            # if (not line.lstrip().startswith('#')
                    # or line.strip() == ''):
                # textCursor.insertText('#')
            # else:
                # textCursor.deletePreviousChar()
            # self.moveCursor(textCursor.Left)
            return True

        if (event.key() == QtCore.Qt.Key_BracketRight
                and event.modifiers() == QtCore.Qt.ControlModifier):
            raise NotImplementedError, 'add indent right here'

        # keyDict = {value:key for key, value in QtCore.Qt.__dict__.iteritems()}
        # print keyDict.get(event.key()), event.text()

        super(CodeEditor, self).keyPressEvent(event)

    #code execution
    def begin_exec(self):
        textCursor = self.textCursor()
        if textCursor.hasSelection():
            text = textCursor.selection().toPlainText()
            if 'nuke' in self._globals.keys():
                self.node_context_exec(text)
            else:
                self.global_exec(text)
        else:
            text = self.toPlainText()
            if 'nuke' in self._globals.keys():
                self.node_context_exec(text)
            else:
                self.global_exec(text)

    def get_node_context(self):
        """
        Use nuke's node stack to 
        determine current node context group.
        Root (top level) by default.
        """
        group = 'root' if not hasattr(self, 'node_context') else self.node_context
        stack = nuke.tcl('stack')
        if stack:
            stack_list = stack.split(' ')
            for item in stack_list:
                if 'node' in item:
                    node = nuke.toNode(item)
                    if not isinstance(node, nuke.PanelNode):
                        node_path = node.fullName()
                        group = 'root' if not '.' in node_path else '.'.join( ['root'] + node_path.split('.')[:-1] )
                        print group
                        return group
        return group

    def node_context_exec(self, text):
        self.node_context = self.get_node_context()
        nuke.toNode(self.node_context).begin()
        self.global_exec(self, text)
        nuke.toNode(self.node_context).end()
        
    def global_exec(self, text):
        #get context
        local = self._locals.copy()
        single = len(text.rstrip().lstrip().split(' ')) == 1
        if single:
            code = compile(text, '<i.d.e>', 'single')
        else:
            code = text
        self.exec_text(code)
        # self.exec_text(text)
        new_locals = {k : self._locals[k] for k in set(self._locals) - set(local)}
        if new_locals and 'import' in text: print new_locals # this should only happen in compile(text, '<string>', 'single') mode

    def exec_text(self, text):
        print '# Result:'
        exec(text, self._globals, self._locals)

    #right click menu items
    # def childEvent(self, event):
    #     print 'CHILD EVENT:', event
    #     super(CodeEditor, self).childEvent(event)
    #     # if isinstance(o, QtGui.QMenu):
    #     #         self.condition = False
    #     #         if e.type() == QtCore.QEvent.ChildAdded:
    #     #             self.menu = o
    #     #             self.menuSetup()

    # def contextMenuEvent(self, event):
    #     print 'CONTEXT MENU EVENT:', event
    #     # print dir(event)
    #     super(CodeEditor, self).contextMenuEvent(event)

        # if e.type() == QtCore.QEvent.ContextMenu:
        #     parent = o.parent()
        #     if bool(parent):
        #         if parent.metaObject().className() == self.scriptInput:
        #             self.condition = True
            # return False

    # def mousePressEvent(self, event):
    #     if event.button() == QtCore.Qt.RightButton:
    #         menu = QtGui.QMenu()
    #         menu.move(QtGui.QCursor().pos())
    #         sublimeNuke = self._globals.get('SublimeNuke')
    #         # local = self._locals.copy()
    #         # self.exec_text('SublimeNuke')
    #         # exec('SublimeNuke', self._globals, new_locals)
    #         # new_locals = {k : self._locals[k] for k in set(self._locals) - set(local)}
    #         # print new_locals
    #         # menu.addAction('Reload', partial(reload,  a))
    #         menu.addAction('Reload', partial(self.reload,  sublimeNuke))
    #         # menu.addAction('Reload', partial(reload,  exec('SublimeNuke', self._globals, self._locals)))
    #         menu.exec_()

    
    # -------------------------------------------------------------------------------
    #shortcuts
    # -------------------------------------------------------------------------------

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    editor = CodeEditor()
    editor.show()
    app.exec_()
