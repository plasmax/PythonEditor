# PythonEditor
A Script Editor for Foundry's NUKE with more features.

[![build](https://github.com/plasmax/PythonEditor/actions/workflows/python-app.yml/badge.svg)](https://github.com/plasmax/PythonEditor/actions/workflows/python-app.yml)

## Installation:
[Download](https://downgit.github.io/#/home?url=https://github.com/plasmax/PythonEditor/tree/master/PythonEditor).
Copy the "PythonEditor" folder from the .zip file into your user .nuke folder.

Create a menu.py file in the .nuke folder and add the following code to it:

```python
import PythonEditor
PythonEditor.nuke_menu_setup(nuke_menu=True, node_menu=True, pane_menu=True)
```

![Screenshot](/media/Screenshot.png)
