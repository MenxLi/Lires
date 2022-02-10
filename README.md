
# Features

![ResBibMan](./resbibman/docs/imgs/ResBibMan.png)
A research literature manager that utilize Bibtex file to record paper information, 
it relies on tags to differentiate papers, and use markdown for notes.

[comment]: <> (## distribution)

[comment]: <> (`python setup.py bdist_wheel --universal`)

# Installation & Usage

Refer to the [docs-CN](./resbibman/docs/使用说明.md) for the usage of this software.

# Future works

## Todo list

- [x] To use TableView of the selection panel
- [ ] Pdf compression - [reference](https://blog.csdn.net/xinRCNN/article/details/113273463)
- [ ] AutoUpdate
- [ ] User info
- [ ] Export database
- [ ] Better way to define time-modified
- [ ] PDF preview

In query widget while importing articles:  

- [x] Add copy from template button
- [ ] Format check

In file selector:

- [x] Add search bar
- [x] Multiple selection
- [x] Right click: export, export bib, delete

Main window:
- [x] Refresh button

settings:

Tags:
- [x] Right click: rename; delete;
- [ ] Drag in to add tag?

### Long time goals

- [ ] Language support

## Known issues

crash when using deletetag or rename tag with tag edit (should supply panel info into the tag_select item)

## Credits:

https://github.com/google/material-design-icons   
https://github.com/GTRONICK/QSS
