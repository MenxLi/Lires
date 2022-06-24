# Resbibman 
Resbibman: a **Res**earch **bib**liograpy **man**ager

<!--![ResBibMan](./resbibman/docs/imgs/ResBibMan.png)-->
![ResBibMan](./resbibman/docs/imgs/mainWindow.png)
A research literature manager that utilize Bibtex file to record paper information, 
it relies on tags to differentiate papers, and use markdown for notes.

It also has server-side module (RBM-web) with a web viewer so that it can be deployed onto a server to share literatures or work in online mode.

[comment]: <> (## distribution)

[comment]: <> (`python setup.py bdist_wheel --universal`)

## Features
* Cross-platform
* Markdown notes, with LaTeX equation support
* Various file formats support, including webpage
* Online mode (remote storage)
* Host a server to view, share and discuss online.

# Installation & Usage

~~Refer to the [docs-CN](./resbibman/docs/UserGuide.md) for the usage of this software.~~

## Installation
```Python
pip install .
rbm-resetconf  # To create default configuration
```

### Update
If you dowload the source code from web url, you can update it with `update.py`  
If you clone it from remote git repository, then please stick with `git pull`

### Docker deployment
Instead of manual installation, The the server side can be deployed and run via docker,   
You may wish to edit `docker-compose.yml` to change port and mount point mapping prior to the following commands
```bash
# update docker container if it's not been built
docker-compose build
# run
docker-compose up
```
To manage access key (for usage see: `rbm-keyman -h`):
```bash
docker exec resbibman rbm-keyman ...
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

**The [docs-CN](./resbibman/docs/UserGuide.md) is helpful but needs more detail. Will add in the fufute**

<!--
## Server usage
Start server with `resbibman -S`  
Access key management with `rbm-keyman`   
Discussion management with `rbm-discuss`
The server serve data at `database` entry of the `resbibman` configration file (`resbibman/conf.json`)
The server port can be assigned at `RBMWeb/backend/conf.json`
-->


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
- [ ] Markdown LaTeX equation support
- [ ] Within software cross-reference
- [ ] Other citation format convert to bibtex
- [ ] Better font size
- [ ] Related works
- [ ] Redirect some logging to status bar
- [ ] Pdf compression - [reference?](https://blog.csdn.net/xinRCNN/article/details/113273463)
- [ ] Export database
- [ ] User info, associate each user with a key in rbm-keyman

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

rbm-collect:
- [ ] web
- [ ] medRxiv
- [ ] bioRxiv
- [ ] PMID

### Long time goals

- ~~[ ] Language support~~
- [ ] Relation graph

## Ideas:
QRunnable for multithreading

</details>

## Known issues
* May crash when changing selection (caused by auto saving)
* Markdown horizontal line highlighter not working somehow
* ~~QWebEngineView may not show html(not work on opensuse and ubuntu22.04?)~~(Solved with PyQt6)

## Credits:
https://github.com/google/material-design-icons   
https://github.com/GTRONICK/QSS
https://github.com/MathJax/MathJax
