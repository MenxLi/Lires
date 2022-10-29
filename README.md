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
```bash
tsc
pip install packages/*
pip install .
```

### Update
If you dowload the source code from web url, you can update it with `update.py`  
If you clone it from remote git repository, then please stick with `git pull`

### Docker deployment
Instead of manual installation, The the RBMWeb server can be deployed via docker,   

You need to edit `docker-compose.yml` to change port and mount point mapping, then execute the following commands to start:
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
To start the RBMWeb server:
```bash
resbibman server
```

For CLI help, see `resbibman -h`  


### Configure
`$RBM_HOME` directory is used for application data storage, by default it is set to `~/.RBM`.  
The data directory contains the configuration file, log files, default database, RBMWeb backend data, cache files...  

To start the application with arbitrary data directory, you can run: 
```bash
export RBM_HOME="your/path/here"; resbibman
```

Other management tools include: 

```bash
rbm-keyman      # Manage access key
rbm-discuss     # Manage online discussions
rbm-collect     # Automatic add entry to database with retriving string
rbm-resetconf   # To reset default configuration
```

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
- [x] Markdown LaTeX equation support
- [x] Export database
- [x] Better font size
- [ ] Advance search
- [ ] Dashboard page
- [ ] Within software cross-reference
- [ ] Other citation format convert to bibtex
- [ ] Related works
- [ ] Redirect some logging to status bar
- [ ] Pdf compression - [reference?](https://blog.csdn.net/xinRCNN/article/details/113273463)
- [ ] ~~ User info, associate each user with a key in rbm-keyman ~~

In query widget while importing articles:  

- [x] Add copy from template button
- [x] Other bibtex template
- [x] Other format convert to bibtex
- [ ] Format check

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

<!-- ## Ideas: -->
<!-- QRunnable for multithreading -->
<!--  -->

</details>

## Known issues

<!-- * May crash when changing selection (caused by auto saving) -->
* Markdown horizontal line highlighter not working somehow
* Adding file may encounter permission error for FAT32 format destination in Linux machine (refer to: [stackoverflow-25716333](https://stackoverflow.com/questions/25716333/))
* ~~QWebEngineView may not show html(not work on opensuse and ubuntu22.04?)~~(Resolved with PyQt6)
* PDFReader based on QWebEngineView may not show PDF (For PyQt6 under Windows, refer to: [stachoverflow-73350761](https://stackoverflow.com/questions/73350761/))

## Credits:
https://github.com/google/material-design-icons   
https://github.com/GTRONICK/QSS  
https://github.com/MathJax/MathJax
