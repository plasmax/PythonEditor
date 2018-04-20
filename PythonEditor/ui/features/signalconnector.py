from __future__ import print_function
from PythonEditor.ui.Qt import QtCore


class SignalConnector(QtCore.QObject):
    """
    Genericized Signal Mapper to connect signals
    of current tabs to functions.
    """
    def __init__(self, parent_widget, use_tabs=True):
        super(SignalConnector, self).__init__()
        self.setObjectName('SignalConnector')
        self.setParent(parent_widget)
        self.parent_widget = parent_widget

        if use_tabs:
            self.editortabs = parent_widget
            tss = self.editortabs.tab_switched_signal
            tss.connect(self.tab_switch_handler)
            self.set_editor()
        else:
            self.editor = parent_widget
            self.connect_signals()

    @QtCore.Slot(int, int, bool)
    def tab_switch_handler(self, previous, current, tabremoved):
        """
        On tab switch, disconnects previous
        tab's signals before connecting the
        new tab.
        """
        if not tabremoved:  # nothing's been deleted
                            # so we need to disconnect
                            # signals from previous editor
            self.disconnect_signals()

        self.set_editor()

    def set_editor(self):
        """
        Sets the current editor
        and connects signals.
        """
        editor = self.editortabs.currentWidget()
        editorChanged = (True if not hasattr(self, 'editor')
                         else self.editor != editor)
        isEditor = editor.objectName() == 'Editor'
        if isEditor and editorChanged:
            self.editor = editor
            self.connect_signals()

    def connect_signals(self):
        """
        For shortcuts that cannot be
        handled directly by QShortcut.
        TODO: as UniqueConnection appears
        to create problems, find another
        connection tracking mechanism.
        """
        editor = self.editor

        editor.tab_signal.connect(self.tab_handler)
        editor.return_signal.connect(self.return_handler)
        editor.wrap_signal.connect(self.wrap_text)
        editor.home_key_ctrl_alt_signal.connect(self.move_to_top)
        editor.end_key_ctrl_alt_signal.connect(self.move_to_bottom)
        editor.ctrl_x_signal.connect(self.cut_line)
        editor.home_key_signal.connect(self.jump_to_start)
        editor.wheel_signal.connect(self.wheel_zoom)
        editor.ctrl_enter_signal.connect(self.exec_selected_text)

    def disconnect_signals(self):
        """
        For shortcuts that cannot be
        handled directly by QShortcut.
        """
        if not hasattr(self, 'editor'):
            return

        editor = self.editor

        editor.tab_signal.disconnect()
        editor.return_signal.disconnect()
        editor.wrap_signal.disconnect()
        editor.home_key_ctrl_alt_signal.disconnect()
        editor.end_key_ctrl_alt_signal.disconnect()
        editor.ctrl_x_signal.disconnect()
        editor.home_key_signal.disconnect()
        editor.wheel_signal.disconnect()
        editor.ctrl_enter_signal.disconnect()
