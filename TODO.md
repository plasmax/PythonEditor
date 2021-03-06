# Python Editor TODO list


#### Bug reports
- [ ] nukeinit.add_to_pane() can cause some widgets to go out of scope and be deleted after they're accessed.
- [ ] Just after saving a file, PythonEditor _sometimes_ will tell me it's not saved when I try to close it.
- [ ] Autocomplete doesn't complete variable names ending in _.
- [ ] Autocomplete doesn't complete first arguments of methods e.g. won't complete "arg" after ( in "".join(arg
- [ ] Sometimes (so far only tested on standalone and in windows...) Ctrl+H will cause the interface to freeze as it is awaiting user input to reveal more information in the program terminal.
- [x] autocomplete doesn't pick up all variables such as asset.properties.value_dict (Fixed: adding properties from the completed object's class as well.)

Within Nuke
- [ ] Startup doesn't redirect streams correctly if panel doesn't open in workspace automatically on startup.
      Steps to reproduce this bug:
      1) Save a workspace that doesn't include PythonEditor on startup (any default will do).
      2) Open a Script Editor and attempt to print to the output. Nothing should appear after # Result.
      3) Open PythonEditor. Streams will be captured and redirected correctly, and the Script Editor once again prints things out.

- [ ] Sometimes the shortcuthandler doesn't override - perhaps when editor doesn't gain focus correctly
- [ ] Shift-enter does not correctly create a new line in the editor and line number display on the left.

Nuke 11 specific
- [ ] In Nuke 11.3v5, closing a tab by clicking the close Button can crash Nuke
- [ ] Workspace doesn't properly recover on Nuke 11
- [x] Right-clicking in the output widget produces two context menus in Nuke 11+

Other
- [ ] Tab may duplicate on save.
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

Resolved
- [x] If script is saved as text somewhere and not edited, a warning message still shows up on close.
- [x] When pressing enter when cursor is here `|    "` the line double-indents.
- [x] Help -> About shows nothing
- [x] Save functions need to be amended to work with new single editor
- [x] Search causes cursor to go missing
- [x] # in string causes rest of line to be greyed out
- [x] Pressing . followed immediately by another key causes the autosave document changed window to appear.
- [x] Shortcuts can be overridden by nuke global shortcuts.
- [x] Single line (selection-based) Ctrl+Enter no longer uses accurate lineno
- [x] CRITICAL BUG: Currently not fully reloadable (error with redirector)
- [x] After saving, close button appears stuck on saved symbol
- [x] Extra indentation occurs in some other programs - this was due to not using a monospaced font.
- [x] Greedy shortcuts override Script Editor when Python Editor is open
- [x] Autocomplete doesn't dissappear when parentheses are typed
- [x] CRITICAL BUG: In rare cases with network disruption the PythonEditorHistory.xml
      can be overwritten with 0 contents. PythonEditor will then not load.
      Add in a pre-check for xml contents in the file (if it exists) and implement
      some sort of backup procedure (e.g. copy to /tmp/ on script close)
- [x] Don't set QT_PREFERRED_BINDING if present.


#### Testing
- [ ] WRITE TESTS. [x] exploratory testing, [ ]  integration testing,
- [ ] Are editor properties correctly kept in sync? Any time a tab name or xml subscript changes, the editor
      should also change. What is the best way to monitor this?
- [ ] Are all function and method names clear in the API?
- [ ] Are all documentation strings up to date and correctly reflect the functions and classes?
- [ ] Thoroughly test that documents in autosave are not updating other documents
- [/] Autocomplete bug when typing inside list comprehension e.g. [nuke.selectedNodes] - partially fixed, doesn't
      autocomplete all names (and only completes every other character!)
- [x] Check that tab closing and then cancelling restores the current tab (without causing disconnect/connect issues)
- [x] Check that tab renaming is consistent with autosave file


#### Features - parity
- [ ] "from module import name 'as' othername", "with ContextManager() 'as' name" - syntax highlight the 'as'
- [ ] Add Script Editor buttons to Menu bar at top - especially fullscreen editor/output,
      which should remember the settings
- [x] Highlight line with error
- [x] Read stdout/stderr on open
- [ ] Echo commands to python editor.
- [ ] Add Script Editor buttons to Menu bar at top - especially fullscreen editor/output,
      which should remember the settings


#### Features - desired
- [ ] Generate PySide2 import for selected text (e.g. "QPalette" would return "from PySide2.QtGui import QPalette")
- [ ] Print Qt5 documentation url (or even better, open browser) for Qt names
- [ ] PythonEditor should be more connected to the filesystem, to encourage tidying up and
      reusing existing scripts.
- [x] alt+b insert #&& 'break'
- [ ] When closing a tab, we should return to the previous tab we were on.
- [ ] Shortcuts Editor should be searchable
- [ ] down arrow should show tabs in searchable QListView side panel not QMenu
- [ ] Open Containing Folder action - default to autosave dir if nothing else
- [ ] Copy File Path action
- [ ] /proc/<pid>/fd/1 & 2 - would these allow a cleaner way of reading stdout that
      overrides the output stream? Is there a windows/Mac equivalent?
- [ ] "Actions" - allow users to create and edit custom scripts that run on editor
      text and are added to the user actions config.
- [ ] Backup PythonEditorHistory.xml button.
- [x] Search and Replace
- [ ] QTreeView/QStandardItemModel snippet
- [ ] Strip whitespace from line endings action
- [ ] Meld diff between tabs and/or tab autosave update warning
- [ ] debugger - needs a traceback parser and an editor view with a list like Pythonista
- [x] Move 'nukefeatures' into an app folder to make it program agnostic.
      True agnosticism would require moving PythonEditorHistory.xml to the user home directory as well.
- [ ] Tab close button [x] should appear on active tab only (like chrome)
      and change width of tab (in proportion to the name) when added (setTabButton, RightSide)
- [x] Move all actions to actions.py and have shortcuts simply setShortcut()
      on the Actions() class, which can be picked up by menus.
- [x] Move tab to start/end
- [ ] Duplicate cursors
- [x] Search box at bottom of editor widget (with "all tabs" checkbox)
- [x] Search across all tabs
- [ ] Projects
- [ ] Autocomplete 'toNode', node.knob() and node[knob]
- [ ] Autocomplete os.environ and other dicts
- [ ] Autocomplete paths if divided by /
- [ ] Projects - the new PYTHONEDITOR_AUTOSAVE_FILE env variable should help.
- [ ] Goto Links in errors/regular paths in the editor
- [ ] Hover over variables to get definition goto, type info, short help()
- [ ] Hover over paths in output window to get goto link
- [ ] Paste into sublime subprocess.Popen('sublime -n --command paste', executable='/bin/tcsh', shell=True)
- [ ] Warn if file has changed on disk (as with autosave when regaining tab focus)
- [ ] Pre-reload PythonEditor safety backup
- [ ] Foldable sidebar with directory tree
- [ ] File Browser with connected file path
- [ ] Recent Files List
- [ ] Implement events or signals to redirect Script Editor stream (for speed)
- [ ] Snippet save actions - write to PythonEditor_snippets.json
- [ ] Writing to external files instead of xml. Keeping those files in tab session until closed with a JSON file
- [ ] Would be nice to highlight line on Ctrl+B execution (of single line)
- [ ] Tabs need QLabels so that they can be italicized when in read_only mode
- [ ] When save dialog comes up, the suggested name should be the tab name/editor.name - and if there's an
      editor path, the dialog should open to that path
- [ ] Preferences - colour
- [ ] Preferences - shortcuts - this has been at least partially accomplished on another branch
- [ ] Preferences - indentation (backspace deletes single space or tab)
- [ ] Preferences - disable autocompletion in comments
- [ ] After updating to saved version of autosave, there should be
      the possibility to undo if replacing with the autosave text wasn't desired.
- [ ] Autocompletion weighting (a la tabtabtab)
- [ ] Add reverse ' = '.join(reversed('sys.stdout = backup'.split(' = ')))
- [ ] GOTO tooltip over selected text
- [ ] Edit Snippets Dialog (for snippets in /.nuke/)
- [x] Tooltip displaying file path when hovering over tabs would be nice. (Easy to implement with QLabels)
- [x] Add menu on the top right corner to select between tabs
- [x] Move all actions to actions.py and have shortcuts simply setShortcut()
      on the Actions() class, which can be picked up by menus.
- [x] Move tab to start/end
- [x] Improve speed of loading tabs
- [/] Set up an execution model where stdout, stderr and stdin are temporarily encapsulated within
      a context managing with statement - is this a good idea?
      it means output will only be shown when text is executed from PythonEditor.
- [x] Snippet file library (currently reads from a file called PythonEditor_snippets.json in .nuke dir if found.)
- [x] Check if there's a better way to connect widgets/objects, synchronously
      (bypassing signal in cases where it's not wanted) - Resolved, starting to use DirectConnection
- [x] Set tab order as a property on the editor and in the autosave
- [x] Small button at right of tab bar with a list of tab names


#### General
- [ ] Test moving TODO.md to github issues (not so great for local)
- [ ] Consider moving snippets to the back of the autocomplete list
- [ ] Prep for release
