from PythonEditor.ui.Qt import QtWidgets, QtCore, QtGui


class ShortcutEditor(QtWidgets.QTreeView):
    """
    A display widget that allows editing of
    keyboard shortcuts assigned to the editor.
    TODO: Make this editable, and reassign shortcuts on edit.
    """
    def __init__(
            self,
            editor=None,
            tabeditor=None,
            terminal=None
        ):
        super(ShortcutEditor, self).__init__()

        model = QtGui.QStandardItemModel()
        self.setModel(model)
        root = model.invisibleRootItem()
        model.setHorizontalHeaderLabels(
            ['Description', 'Shortcut', 'About']
            )

        self.header().setStretchLastSection(False)
        rtc = QtWidgets.QHeaderView.ResizeToContents
        try:
            self.header().setResizeMode(rtc)
        except AttributeError:
            # 'PySide2.QtWidgets.QHeaderView' object has no attribute 'setResizeMode'
            # TODO: Find compatible way to resize header.
            pass

        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint
        )
        self.setUniformRowHeights(True)
        self.resize(800, 600)

        widgets = []
        if editor is not None:
            widgets.append(editor)
        if terminal is not None:
            widgets.append(terminal)
        if tabeditor is not None:
            widgets.append(tabeditor)

        for widget in widgets:
            for action in widget.actions():
                name = action.text()
                # TODO: put shortcut in a keycatcher widget.
                shortcut = action.shortcut().toString()
                about = ' '.join([
                    line.strip() for line in
                    action.toolTip().splitlines()
                    ]).strip()
                row = [
                QtGui.QStandardItem(val)
                for val in [name, shortcut, about]
                ]
                root.appendRow(row)