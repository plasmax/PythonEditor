from PythonEditor.ui.editor import Editor
import nuke

class EditorKnob(Editor):
    """
    TODO: needs a mechanism to switch/write to its own callback knobs
    and a method to execute from within node context (aka button)
    """
    def __init__(self, node=None):
        super(EditorKnob, self).__init__(self)
        self.text_changed_signal.connect(self.valueChanged)
        self.node = node
        self.read()

    def knob_check(self):
        if not self.node.knob('code'):
            self.node.addKnob(
                nuke.PyScript_Knob(
                    'code',
                    'Execute Code',
                    ''
                )
            )

    def read(self):
        self.knob_check()
        self.setPlainText(self.node.knob('code').value())

    def makeUI(self):
        return self

    def valueChanged(self):
        self.knob_check()
        self.node['code'].setValue(self.toPlainText())
