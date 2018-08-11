# Python Editor TODO list


#### Bug fixes
- [x] Extra indentation occurs in some other programs - this was due to not using a monospaced font.
- [ ] Word wrapping and blocks can cause errors, especially in moving text up/down
- [ ] Greedy shortcuts override Script Editor when Python Editor is open
- [ ] Tooltip colour permanently set in autocompletion
- [ ] Search causes cursor to go missing
- [ ] # in string causes rest of line to be greyed out


#### Testing
- [x] Check that tab closing and then cancelling restores the current tab (without causing disconnect/connect issues)
- [ ] Check that tab renaming is consistent with autosave file
- [ ] Are editor properties correctly kept in sync? Any time a tab name or xml subscript changes, the editor
      should also change. What is the best way to monitor this?
- [ ] Are all function and method names clear in the API?
- [ ] Are all documentation strings up to date and correctly reflect the functions and classes?
- [ ] Thoroughly test that documents in autosave are not updating other documents
- [/] Autocomplete bug when typing inside list comprehension e.g. [nuke.selectedNodes] - partially fixed, doesn't
      autocomplete all names (and only completes every other character!)

#### Features - parity
- [x] Highlight line with error
- [ ] Read stdout/stderr on open (redirect stdout to Queue)
- [ ] Add Script Editor buttons to Menu bar


#### Features - desired
- [ ] Foldable sidebar with directory tree
- [ ] File Browser with connected file path
- [ ] Recent Files List
- [ ] Implement events or signals to redirect Script Editor stream (for speed)
- [x] Snippet file library
- [ ] Writing to external files instead of xml. Keeping those files in tab session until closed with a JSON file
- [x] Check if there's a better way to connect widgets/objects, synchronously
      (bypassing signal in cases where it's not wanted) - Resolved, starting to use DirectConnection
- [x] Set tab order as a property on the editor and in the autosave
- [ ] Set up an execution model where stdout, stderr and stdin are temporarily encapsulated within a context managing with
      statement - is this a good idea? it means output will only be shown when text is executed from PythonEditor.
- [ ] Would be nice to highlight line on Ctrl+B execution (of single line)
- [ ] Tabs need QLabels so that they can be italicized when in read_only mode
- [ ] Tooltip displaying file path when hovering over tabs would be nice. (Easy to implement with QLabels)
- [ ] When save dialog comes up, the suggested name should be the tab name/editor.name - and if there's an
      editor path, the dialog should open to that path
- [ ] Add menu on the top right corner to select between tabs
- [ ] Preferences - colour
- [ ] Preferences - shortcuts
- [ ] Preferences - indentation (backspace deletes single space or tab)
- [ ] Preferences - disable autocompletion in comments
- [ ] Warn if file has changed on disk (as with autosave when regaining tab focus)
- [x] Small button at right of tab bar with a list of tab names
- [ ] After updating to saved version of autosave, there should be a possibility to undo if replacing with the autosave text wasn't desired.
- [ ] Autocompletion weighting (a la tabtabtab)
- [ ] Add reverse ' = '.join(reversed('sys.stdout = backup'.split(' = ')))
- [ ] GOTO tooltip over selected text
- [ ] Edit Snippets Dialog (for snippets in /.nuke/)
- [ ] Improve speed by loading tabs separately
- [ ] Duplicate cursors
- [ ] Search box at bottom of editor widget


#### General
- [ ] Test moving TODO.md to github issues (not so great for local)


