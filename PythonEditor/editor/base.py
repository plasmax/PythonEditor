import os
import sys
import re
import time
print 'importing', __name__, 'at', time.asctime()

print sys.version
print sys.executable

try:
    import nuke
except ImportError:
    pass
    
from qt import QtGui, QtCore

from features import syntaxhighlighter

class CodeEditor(QtGui.QPlainTextEdit):
    clearOutput = QtCore.Signal()

    def __init__(self, file, output):
        super(CodeEditor, self).__init__()
        self._globals = dict()
        self._locals = dict()
        self._file = file

        self.clearOutput.connect(output.clear)

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

    def showEvent(self, event):
        try:
            self.setup_env()
        except NameError, e:
            print e
            import inspect
            caller_globals = dict(inspect.getmembers(inspect.stack()[1][0]))['f_globals']
            self._globals = caller_globals
            if 'SIMULATION' in self._globals:
                print self._globals['SIMULATION']
            self._locals = locals()
        super(CodeEditor, self).showEvent(event)

    def setup_env(self):
        nuke.tcl('python -exec "PythonEditor.editor.base._globals = globals()"')
        nuke.tcl('python -exec "PythonEditor.editor.base._locals = locals()"')

        self._globals = _globals
        self._locals = _locals
        self._locals.update({'__instance':self})#this will only refer to the latest instance; not sure how useful that is.

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
                indentCount = len(str(line)) - len(str(line).lstrip(' '))
                textCursor.insertText('\n'+' '*indentCount)
                return True

        if event.key() in (QtCore.Qt.Key_Backspace,):
            if event.modifiers() == QtCore.Qt.ControlModifier:
                self.clearOutput.emit()
                return True

        if event.key() == QtCore.Qt.Key_Tab:
            textCursor = self.textCursor()
            if textCursor.hasSelection():
                safe_string = textCursor.selectedText().replace(u'\u2029', '\n')
                newLines = (len(safe_string.split('\n')) > 1)
                if newLines:
                    raise NotImplementedError, 'add indent multiple lines here'
                    return True
            textCursor.insertText('    ')
   
        if (event.key() == QtCore.Qt.Key_Slash
                and event.modifiers() == QtCore.Qt.ControlModifier):
            textCursor = self.textCursor()

            #get line numbers
            blockNumbers = set([
                    self.document().findBlock(b).blockNumber()
                    for b in range(textCursor.selectionStart(), textCursor.selectionEnd())
                        ])
            blockNumbers |= set([self.document().findBlock(textCursor.position()).blockNumber()])
            blocks = [
                    self.document().findBlockByNumber(b)
                    for b in blockNumbers
                    if self.document().findBlockByNumber(b).text() != ''
                    ]
            
            #iterate through lines in doc commenting or uncommenting based on whether everything is commented or not
            commentAllOut = any([not str(block.text()).lstrip().startswith('#') for block in blocks])
            if commentAllOut:
                for block in blocks:
                    cursor = QtGui.QTextCursor(block)
                    cursor.movePosition(textCursor.StartOfLine)
                    cursor.insertText('#')
            else:
                for block in blocks:
                    cursor = QtGui.QTextCursor(block)
                    cursor.select(QtGui.QTextCursor.LineUnderCursor)
                    selectedText = cursor.selectedText()
                    newText = str(selectedText).replace('#', '', 1)
                    cursor.insertText(newText)
            return True

        if (event.key() == QtCore.Qt.Key_BracketRight
                and event.modifiers() == QtCore.Qt.ControlModifier):
            raise NotImplementedError, 'add right indent here'

        if (event.key() == QtCore.Qt.Key_BracketLeft
                and event.modifiers() == QtCore.Qt.ControlModifier):
            raise NotImplementedError, 'add left indent here'

        if (event.key() == QtCore.Qt.Key_K
                and event.modifiers() == QtCore.Qt.ShiftModifier | QtCore.Qt.ControlModifier):
            raise NotImplementedError, 'add delete line'

        if (event.key() == QtCore.Qt.Key_F
                and event.modifiers() == QtCore.Qt.ControlModifier):
            raise NotImplementedError, 'add search function'

        if (event.key() == QtCore.Qt.Key_H
                and event.modifiers() == QtCore.Qt.ControlModifier):
            textCursor = self.textCursor()
            if textCursor.hasSelection():
                text = textCursor.selection().toPlainText()
                cmd = 'help(' + text + ')'
                self.global_exec(cmd)

        if (event.key() == QtCore.Qt.Key_T
                and event.modifiers() == QtCore.Qt.ControlModifier):
            textCursor = self.textCursor()
            if textCursor.hasSelection():
                text = textCursor.selection().toPlainText()
                cmd = 'type(' + text + ')'
                self.global_exec(cmd)

        if (event.key() == QtCore.Qt.Key_S
                and event.modifiers() == QtCore.Qt.ControlModifier | QtCore.Qt.AltModifier):
            event.accept()
            raise NotImplementedError, 'add save function'

        if (event.key() == QtCore.Qt.Key_D
                and event.modifiers() == QtCore.Qt.ControlModifier):
            raise NotImplementedError, 'add select duplicate function'

        if (event.key() == QtCore.Qt.Key_Home
                and event.modifiers() == QtCore.Qt.ControlModifier | QtCore.Qt.AltModifier):
            raise NotImplementedError, 'add move line to top function'

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
        self.global_exec(text)
        nuke.toNode(self.node_context).end()
        
    def global_exec(self, text):
        #get context
        local = self._locals.copy()
        single = len(text.rstrip().lstrip().split(' ')) == 1
        if single:
            code = compile(text, '<i.d.e>', 'single')
        else:
            code = compile(text, '<i.d.e>', 'exec')

        self.exec_text(code)

        # new_locals = {k:self._locals[k] for k in set(self._locals) - set(local)}
        new_locals = dict()
        for k in set(self._locals) - set(local):
            new_locals[k] = self._locals[k]
        
        if new_locals and 'import' in text: 
            print new_locals # this should only happen in compile(text, '<string>', 'single') mode

    def exec_text(self, text):
        print '# Result:'
        exec(text, self._globals, self._locals)

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()

        self.node_context = self.get_node_context()
        with nuke.toNode(self.node_context):
            pythonknobs = [k for k in nuke.selectedNode().allKnobs()
                            if type(k) in (nuke.PyScript_Knob,
                                          nuke.PythonKnob)]
            for knob in pythonknobs:
                menu.addAction('Load {0}'.format(knob.name()), lambda k=knob: nuke.message(k.value()))


        menu.exec_(QtGui.QCursor().pos())

    # -------------------------------------------------------------------------------
    #shortcuts
    # -------------------------------------------------------------------------------

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    editor = CodeEditor()
    editor.show()
    app.exec_()
