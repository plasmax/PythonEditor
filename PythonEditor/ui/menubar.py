
import os # temporary for self.open until files.py or files/open.py, save.py, autosave.py implemented.
import uuid

from PythonEditor.ui.Qt import QtWidgets
from PythonEditor.ui.features import actions
from PythonEditor.utils import save
from PythonEditor._version import __version__


class MenuBar(object):
    """
    Install a menu on the given widget.
    """
    def __init__(self, widget):
        self.pythoneditor = widget
        self.tabeditor = widget.tabeditor
        self.tabs = widget.tabeditor.tabs
        self.editor = widget.tabeditor.editor
        self.terminal = widget.terminal
        self.menu_setup()

    def menu_setup(self):
        """
        Adds top menu bar and various menu
        items based on a json config file.
        """
        self.menu = QtWidgets.QMenuBar(self.pythoneditor)
        names = [
            'File',
            'Edit',
            'View',
            'Tools',
            'Find',
            'Selection',
            'Preferences',
            'Help',
        ]
        for name in names:
            self.menu.addMenu(name)

        for widget, action_name, attributes in actions.class_actions(self):
            location = attributes.get('Menu Location')
            if location is None:
                continue
            for action in widget.actions():
                if action.text() != action_name:
                    continue
                break
            else:
                continue

            menu = self.menu
            if location.strip():
                for name in location.split('/'):
                    item = actions.find_menu_item(menu, name)
                    if item is None:
                        item = menu.addMenu(name)
                    menu = item
                menu.addAction(action)

        self.pythoneditor.layout().insertWidget(0, self.menu)
