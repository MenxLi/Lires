# Features

**My research literature manager**  

<!--![ResBibMan](./resbibman/docs/imgs/ResBibMan.png)-->
![ResBibMan](./resbibman/docs/imgs/mainWindow.png)
A research literature manager that utilize Bibtex file to record paper information, 
it relies on tags to differentiate papers, and use markdown for notes.

It also has server-side module (RBM-web) with a web viewer so that it can be deployed onto a server to share literatures or work in online mode.

[comment]: <> (## distribution)

[comment]: <> (`python setup.py bdist_wheel --universal`)

# Installation & Usage

~~Refer to the [docs-CN](./resbibman/docs/使用说明.md) for the usage of this software.~~

## Installation
```Python
pip install .
rbm-resetconf  # To create default configuration
```

## Usage:
To start the main program:
```bash
resbibman
```
For CLI help, see `resbibman -h`  
Other CLI command includes:
```bash
rbm-keyman      # Manage access key
rbm-discuss     # Manage online discussions
rbm-collect     # Automatic add entry to database with retriving string
```


**The [docs-CN](./resbibman/docs/使用说明.md) is helpful but needs more detail. Will add in the fufute**

## Server usage
Start server with `resbibman -S`  
Access key management with` rbm-keyman `  
The server serve data at `database` entry of the `resbibman` configration file (`resbibman/conf.json`)
The server port can be assigned at `RBMWeb/backend/conf.json`

# Future works

<details>
<summary> Future works</summary>

## Todo list

- [x] To use TableView of the selection panel
- [x] PDF cover preview
- [x] Change bib
- [x] Use cache to accelerate pdf preview
- [x] Better way to define time-modified
- [x] Online discussion / View comments online (Use sqlite to save discussion on server side)
- [ ] Dashboard page
- [ ] Better font size
- [ ] Redirect some logging to status bar
- [ ] Other citation format convert to bibtex
- [ ] Pdf compression - [reference?](https://blog.csdn.net/xinRCNN/article/details/113273463)
- [ ] Export database
- [ ] ~~User info, associate each user with a key in rbm-keyman~~

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
- [ ] Sub-tags (Cascading tags / Nested tags)

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
