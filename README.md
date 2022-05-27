# Features

**My research literature manager**  

![ResBibMan](./resbibman/docs/imgs/ResBibMan.png)
A research literature manager that utilize Bibtex file to record paper information, 
it relies on tags to differentiate papers, and use markdown for notes.

It also has a web viewer (RBM-web) so that it can be deployed into a server to share literatures.

[comment]: <> (## distribution)

[comment]: <> (`python setup.py bdist_wheel --universal`)

# Installation & Usage

~~Refer to the [docs-CN](./resbibman/docs/使用说明.md) for the usage of this software.~~

## Installation
```Python
pip install .
resbibman --reset_conf  # To create default configuration
```

## Usage:
See `resbibman -h`  
Refer to the [docs-CN](./resbibman/docs/使用说明.md)  

**This reference is outdated, new versions will be added in the future**

# Future works

<details>
<summary> Future works</summary>

## Todo list

- [x] To use TableView of the selection panel
- [x] PDF cover preview
- [x] Change bib
- [x] Use cache to accelerate pdf preview
- [x] Better way to define time-modified
- [ ] Redirect some logging to status bar
- [ ] Other citation format convert to bibtex
- [ ] Pdf compression - [reference?](https://blog.csdn.net/xinRCNN/article/details/113273463)
- [ ] User info
- [ ] Export database
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
- [ ] Right click: open url, free local

Main window:
- [x] Refresh button

settings:

Tags:
- [x] Right click: rename; delete;
- [ ] Sub-tags

Refractor:
- [ ] Move more methods into core classes

### Long time goals

- ~~[ ] Language support~~
- [ ] Relation graph

## Ideas:
QRunnable for multithreading

</details>

## Known issues
* May crash when changing selection (caused by auto saving)
* QWebEngineView may not show html(not work on opensuse and ubuntu22.04?)
* Markdown horizontal line highlighter not working somehow

## Credits:
https://github.com/google/material-design-icons   
https://github.com/GTRONICK/QSS
