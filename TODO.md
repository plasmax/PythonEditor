# Python Editor TODO list

#### Bug fixes
- [ ] Extra indentation occurs in some other programs
- [ ] Word wrapping and blocks can cause errors, especially in moving text up/down


#### Testing
- [x] Check that tab closing and then cancelling restores the current tab (without causing disconnect/connect issues)
- [ ] Check that tab renaming is consistent with autosave file
- [ ] Are editor properties correctly kept in sync? Any time a tab name or xml subscript changes, the editor should also change. What is the best way to monitor this?
- [ ] Are all function and method names clear in the API?
- [ ] Are all documentation strings up to date and correctly reflect the functions and classes?
- [ ] Thoroughly test that documents in autosave are not updating other documents

#### Features - parity
- [x] Highlight line with error
- [ ] Read stdout/stderr on open (redirect stdout to log file?)


#### Features - desired
- [ ] Foldable sidebar with directory tree
- [ ] File Browser with connected file path
- [ ] Using signal/slot to redirect stream is slower than desirable
- [ ] Snippet file library
- [ ] Writing to external files instead of xml. Keeping those files in tab session until closed with a JSON file
- [x] Check if there's a better way to connect widgets/objects, synchronously (bypassing signal in cases where it's not wanted) - Resolved, starting to use DirectConnection 
- [ ] Set tab order as a property on the editor and in the autosave
- [ ] Set up an execution model where stdout, stderr and stdin are temporarily encapsulated within a context managing with statement - is this a good idea? it means output will only be shown when text is executed from PythonEditor. 
- [ ] Would be nice to highlight line on Ctrl+B execution (of single line)
- [ ] Tabs need QLabels so that they can be italicized when in read_only mode
- [ ] Tooltip displaying file path when hovering over tabs would be nice. (Easy to implement with QLabels)
- [ ] When save dialog comes up, the suggested name should be the tab name/editor.name - and i

#### General
- [ ] Test moving TODO.md to github issues (not so great for local)

