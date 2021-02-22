# Python Editor TODO list


## Bug reports
- [ ] nukeinit.add_to_pane() can cause some widgets to go out of scope and be deleted after they're accessed.
- [ ] Just after saving a file, PythonEditor _sometimes_ will tell me it's not saved when I try to close it.
- [ ] Autocomplete doesn't complete variable names ending in _.
- [ ] Autocomplete doesn't complete first arguments of methods e.g. won't complete "arg" after ( in "".join(arg
- [ ] Sometimes (so far only tested on standalone and in windows...) Ctrl+H will cause the interface to freeze as it is awaiting user input to reveal more information in the program terminal.
- [x] ~autocomplete doesn't pick up all variables such as asset.properties.value_dict (Fixed: adding properties from the completed object's class as well.)~
### Within Nuke
- [ ] Startup doesn't redirect streams correctly if panel doesn't open in workspace automatically on startup.
      Steps to reproduce this bug:
      1) Save a workspace that doesn't include PythonEditor on startup (any default will do).
      2) Open a Script Editor and attempt to print to the output. Nothing should appear after # Result.
      3) Open PythonEditor. Streams will be captured and redirected correctly, and the Script Editor once again prints things out.

- [ ] Sometimes the shortcuthandler doesn't override - perhaps when editor doesn't gain focus correctly
- [ ] Shift-enter does not correctly create a new line in the editor and line number display on the left.
### Nuke 11 specific
- [ ] In Nuke 11.3v5, closing a tab by clicking the close Button can crash Nuke
- [ ] Workspace doesn't properly recover on Nuke 11
- [x] ~Right-clicking in the output widget produces two context menus in Nuke 11+~
### Other
- [ ] Close button should be persistent on the active tab.
- [ ] Sometimes wrong tab may be clicked
- [ ] Confirm overwrite file on save.
- [ ] When editing a document across multiple instances, updating to latest autosave sometimes triggers twice.
- [ ] Alt-tabbing quickly away from and back to the editor causes an autosave message. call autosave() on focusOutEvent to ensure save.
- [ ] Opening a file doesn't prevent its contents from being autosaved. If not modified, files should be read-only.
- [ ] The same file opened twice will open two separate tabs.
- [ ] Ctrl+F doesn't update word highlighting selection.
- [ ] Minor - Clicking on a tab to the right of the QLineEdit when editing a tab name causes a jump, and the wrong tab to be selected.
- [ ] Select between brackets only works for round brackets
- [ ] On first open (if not pinned to layout), tab may not display contents
- [ ] Word wrapping and blocks can cause errors, especially in moving text up/down
- [ ] Tooltip colour permanently set in autocompletion
- [ ] Double printing to sys.stdout (/probably/ caused by writing to sys.__stdout__ as well as outputRedirector)
- [ ] Override setPlainText to avoid string encoding errors (can this affect copy paste?)
- [?] Save functions need to be amended to work with new single editor
### Resolved
- [x] ~Tab may duplicate on save.~
- [x] ~If script is saved as text somewhere and not edited, a warning message still shows up on close.~
- [x] ~When pressing enter when cursor is here `|    "` the line double-indents.~
- [x] ~Help -> About shows nothing~
- [x] ~Save functions need to be amended to work with new single editor~
- [x] ~Search causes cursor to go missing~
- [x] ~# in string causes rest of line to be greyed out~
- [x] ~Pressing . followed immediately by another key causes the autosave document changed window to appear.~
- [x] ~Shortcuts can be overridden by nuke global shortcuts.~
- [x] ~Single line (selection-based) Ctrl+Enter no longer uses accurate lineno~
- [x] ~CRITICAL BUG: Currently not fully reloadable (error with redirector)~
- [x] ~After saving, close button appears stuck on saved symbol~
- [x] ~Extra indentation occurs in some other programs - this was due to not using a monospaced font.~
- [x] ~Greedy shortcuts override Script Editor when Python Editor is open~
- [x] ~Autocomplete doesn't dissappear when parentheses are typed~
- [x] ~CRITICAL BUG: In rare cases with network disruption the PythonEditorHistory.xml~
      can be overwritten with 0 contents. PythonEditor will then not load.
      Add in a pre-check for xml contents in the file (if it exists) and implement
      some sort of backup procedure (e.g. copy to /tmp/ on script close)
- [x] ~Don't set QT_PREFERRED_BINDING if present.~


## Testing
- [ ] WRITE TESTS. [x] integration tests, [ ] unit tests, [ ] regression tests
- [ ] Are editor properties correctly kept in sync? Any time a tab name or xml subscript changes, the editor
      should also change. What is the best way to monitor this?
- [ ] Are all function and method names clear in the API?
- [ ] Are all documentation strings up to date and correctly reflect the functions and classes?
- [ ] Thoroughly test that documents in autosave are not updating other documents
- [/] Autocomplete bug when typing inside list comprehension e.g. [nuke.selectedNodes] - partially fixed, doesn't
      autocomplete all names (and only completes every other character!)
- [x] ~Check that tab closing and then cancelling restores the current tab (without causing disconnect/connect issues)~
- [x] ~Check that tab renaming is consistent with autosave file~


## Features - parity
- [ ] "from module import name 'as' othername", "with ContextManager() 'as' name" - syntax highlight the 'as'
- [ ] Add Script Editor buttons to Menu bar at top - especially fullscreen editor/output,
      which should remember the settings
- [x] ~Highlight line with error~
- [x] ~Read stdout/stderr on open~
- [ ] Echo commands to python editor (eventFilter watch script editor)
- [ ] Add Script Editor buttons to Menu bar at top - especially fullscreen editor/output,
      which should remember the settings


## Features - desired
- [ ] Popup labels or warning indicators on the status bar instead of over the top of the editor.
- [ ] Breakpoints/trace points in linenumberarea
### Projects
- [ ] Projects are just a list of autosave files - hop between them with Ctrl+Alt+P
- [ ] Tearable tabs - tearing off a tab adds it to a new instance of PythonEditor (a new Project)
- [ ] PythonEditor should be more connected to the filesystem, to encourage tidying up and
      reusing existing scripts.
- [ ] Recent Files List
- [ ] Foldable sidebar with directory tree
- [ ] File Browser with connected file path
- [ ] Writing to external files instead of xml. Keeping those files in tab session until closed with a JSON file
- [ ] Italicize tabs/list items when in read_only mode
- [ ] Warn if file has changed on disk (as with autosave when regaining tab focus)
### Gotos
- [ ] Goto previous cursor position shortcut
- [ ] Goto Links in errors/regular paths in the editor
- [ ] GOTO tooltip over selected text
- [ ] Hover over paths in output window to get goto link
- [ ] Hover over variables to get definition goto, type info, short help()
### Preferences
- [ ] Preferences - colour
- [ ] Preferences - shortcuts - this has been at least partially accomplished on another branch
- [ ] Preferences - indentation (backspace deletes single space or tab)
- [ ] Preferences - disable autocompletion in comments
### Autocomplete
- [ ] Autocomplete 'toNode', node.knob() and node[knob]
- [ ] Autocomplete os.environ and other dicts
- [ ] Autocomplete paths if divided by /
- [ ] Autocompletion weighting (a la tabtabtab)
### Actions
- [ ] Add reverse ' = '.join(reversed('sys.stdout = backup'.split(' = ')))
- [ ] Open Containing Folder action - default to autosave dir if nothing else
- [ ] Paste into sublime subprocess.Popen('sublime -n --command paste', executable='/bin/tcsh', shell=True)
### Snippets
- [ ] QTreeView/QStandardItemModel snippet
- [ ] Edit Snippets Dialog (for snippets in /.nuke/)
### Documentation
- [ ] Generate PySide2 import for selected text (e.g. "QPalette" would return "from PySide2.QtGui import QPalette")
- [ ] Print Qt5 documentation url (or even better, open browser) for Qt names
### Other
- [ ] "Code Actions" - allow users to create and edit custom scripts that run on editor
      text and are added to the user actions config.
- [ ] debugger - needs a traceback parser and an editor view with a list like Pythonista
- [ ] Duplicate cursors
- [ ] Pre-reload PythonEditor safety backup
- [ ] Implement events or signals to redirect Script Editor stream (for speed)
- [ ] When save dialog comes up, the suggested name should be the tab name/editor.name - and if there's an
      editor path, the dialog should open to that path
- [x] ~Make "Update from Autosave" undoable.~
- [x] ~alt+b insert #&& 'break'~
- [x] ~When closing a tab, we should return to the previous tab we were on.~
- [x] ~down arrow should show tabs in searchable QListView side panel not QMenu~
- [x] ~Copy File Path action~
- [x] ~Backup PythonEditorHistory.xml button.~
- [x] ~Search and Replace~
- [x] ~Strip whitespace from line endings action~
- [x] ~Diff between tabs and/or tab autosave update warning~
- [x] ~Move 'nukefeatures' into an app folder to make it program agnostic.~
      ~True agnosticism would require moving PythonEditorHistory.xml to the user home directory as well.~
- [x] ~Tab close button [x] should appear on active tab only (like chrome)~
      ~and change width of tab (in proportion to the name) when added (setTabButton, RightSide)~
- [x] ~Move all actions to actions.py and have shortcuts simply setShortcut()~
      ~on the Actions() class, which can be picked up by menus.~
- [x] ~Move tab to start/end~
- [x] ~Search box at bottom of editor widget (with "all tabs" checkbox)~
- [x] ~Search across all tabs~
- [x] ~Snippet save actions - write to PythonEditor_snippets.json~
- [x] ~Tooltip displaying file path when hovering over tabs would be nice. (Easy to implement with QLabels)~
- [x] ~Add menu on the top right corner to select between tabs~
- [x] ~Move all actions to actions.py and have shortcuts simply setShortcut()~
      on the Actions() class, which can be picked up by menus.
- [x] ~Move tab to start/end~
- [x] ~Improve speed of loading tabs~
- [x] ~Snippet file library (currently reads from a file called PythonEditor_snippets.json in .nuke dir if found.)~
- [x] ~Check if there's a better way to connect widgets/objects, synchronously~
      ~(bypassing signal in cases where it's not wanted) - Resolved, starting to use DirectConnection~
- [x] ~Set tab order as a property on the editor and in the autosave~
- [x] ~Small button at right of tab bar with a list of tab names~

## Rejected
- [/] ~/proc/<pid>/fd/1 & 2 - would these allow a cleaner way of reading stdout that~
      ~overrides the output stream? Is there a windows/Mac equivalent?~ - No.
- [/] ~Set up an execution model where stdout, stderr and stdin are temporarily encapsulated within~
      ~a context managing with statement - is this a good idea?~
      ~it means output will only be shown when text is executed from PythonEditor.~
- [/] ~Shortcuts Editor should be searchable~
      It's now sortable, which is as useful as it needs to be, really.
- [/] ~Test moving TODO.md to github issues (not so great for local)~ - Maybe some of them, but this list is easier to update.
- [/] ~Consider moving snippets to the back of the autocomplete list~ - Rejected - they're too useful

## General
- [ ] Prep for release
