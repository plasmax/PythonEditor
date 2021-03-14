import nuke
from PythonEditor.ui import editor


class PyKnobEdit(editor.Editor):
    """
    Editor that automatically updates knobs.
    """
    def __init__(self, node=None, knob=None):
        super(PyKnobEdit, self).__init__()
        self.node = node

        knob = node.knob('py_btn') if knob is None else knob
        if knob is None:
            return
        self.knob = knob

        self.read()
        self.text_changed_signal.connect(self.write)

    def makeUI(self):
        return self

    def read(self):
        self.setPlainText(self.knob.value())

    def write(self):
        self.knob.setValue(self.toPlainText())


def create_jupyter_node(exec_cmd=''):
    noop = nuke.nodes.NoOp(name='Jupyter_Node')
    pybtn = nuke.PyScript_Knob('py_btn', 'Execute Code')
    pybtn.setFlag(nuke.STARTLINE)
    pytreebtn = nuke.PyScript_Knob('py_tree_btn', 'Execute Tree', exec_cmd)
    pyknob = nuke.PyCustom_Knob('py_edit', '', 'PyKnobEdit(node=nuke.thisNode())')

    for knob in pyknob, pybtn, pytreebtn:
        noop.addKnob(knob)

    userknob = noop.knob('User')
    userknob.setLabel('Python')

exec_tree = """# exec connected jupyter nodes
def node_tree(node):
    nodes = []
    while node is not None:
        if node.knob('py_btn'):
            nodes.append(node)
        node = node.input(0)
    return reversed(nodes)

def exec_tree_btns():
    for node in node_tree(nuke.thisNode()):
        node.knob('py_btn').execute()

exec_tree_btns()
"""

# create_jupyter_node(exec_cmd=exec_tree)


