
import os # temporary for self.open until files.py or files/open.py, save.py, autosave.py implemented.
import uuid
from PythonEditor.ui.Qt import QtWidgets
from PythonEditor.utils import save
from PythonEditor.ui.features import actions
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

        action_dict = actions.load_actions_from_json()
        for widget_name, widget_actions in action_dict.items():
            if not hasattr(self, widget_name):
                # TODO: might want to do something interesting
                # here with state - instead of widget
                # attrib, get 'widget clicked on'
                continue
            widget = getattr(self, widget_name)
            if widget is None:
                continue
            for action_name, attributes in widget_actions.items():
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
                if location != '':
                    for name in location.split('/'):
                        item = actions.find_menu_item(menu, name)
                        if item is None:
                            item = menu.addMenu(name)
                        menu = item
                    menu.addAction(action)

        self.pythoneditor.layout().insertWidget(0, self.menu)
