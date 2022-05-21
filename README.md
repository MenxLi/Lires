# Features

**My research literature manager**  

![ResBibMan](./resbibman/docs/imgs/ResBibMan.png)
A research literature manager that utilize Bibtex file to record paper information, 
it relies on tags to differentiate papers, and use markdown for notes.

It also has a web viewer (RBM-web) so that it can be deployed into a server to share literatures.

[comment]: <> (## distribution)

[comment]: <> (`python setup.py bdist_wheel --universal`)

# Installation & Usage

Refer to the [docs-CN](./resbibman/docs/使用说明.md) for the usage of this software.

# Future works

<details>
<summary> Future works</summary>

## Todo list

- [x] To use TableView of the selection panel
- [x] PDF cover preview
- [x] Change bib
- [ ] Use cache to accelerate
- [ ] Other citation format convert to bibtex
- [ ] Pdf compression - [reference?](https://blog.csdn.net/xinRCNN/article/details/113273463)
- [ ] User info
- [ ] Export database
- [ ] Better way to define time-modified
- [ ] View comments online

In query widget while importing articles:  

- [x] Add copy from template button
- [x] Other bibtex template
- [ ] Format check
- [ ] Other format convert to bibtex

In file selector:

- [x] Add search bar
- [x] Multiple selection
- [x] Right click: export, export bib, delete
- [ ] Right click: open url

Main window:
- [x] Refresh button

settings:

Tags:
- [x] Right click: rename; delete;

Code structure change:
- [ ] Move more methods into core classes

### Long time goals

- [ ] Language support

</details>

## Known issues
* May crash when changing selection (caused by auto saving)
* QWebEngineView may not show html(not work on opensuse and ubuntu22.04?)
* Markdown horizontal line highlighter not working somehow

## Credits:
https://github.com/google/material-design-icons   
https://github.com/GTRONICK/QSS
