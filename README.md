# Resbibman 
Resbibman: a **Res**earch **bib**liograpy **man**ager

<!--![ResBibMan](./resbibman/docs/imgs/ResBibMan.png)-->
<!--![ResBibMan](./resbibman/docs/imgs/mainWindow.png)-->
![ResBibMan](http://limengxun.com/files/imgs/resbibman.png)
A research literature manager that utilize Bibtex file to record paper information, 
it relies on tags to differentiate papers, and use markdown for notes.

It also has server modules: resbibman-server (RBM server) with a web viewer (RBMWeb) so that it can be deployed onto a server to share literatures or work in online mode.

[comment]: <> (## distribution)

[comment]: <> (`python setup.py bdist_wheel --universal`)

## Features
* Cross-platform
* Cascading tags  
* Markdown notes, with LaTeX equation support
* Online mode (remote storage)
* Host a server to view, share and discuss online
* Multi-user permission management
* AI-powered features (iRBM)

# Installation & Usage
## Installation
installation for client-side GUI only:
> **Prerequisites:**  Python 3.8+
```bash
pip install setuptools wheel pyyaml
pip install packages/QFlowLayout packages/QCollapsibleCheckList
pip install .
rbm-utils download_pdfjs                # [optional] download pdf.js viewer to view pdf inside resbibman
# pip install ".[ai]"                   # [optional] to install with AI dependencies
```
installation for server and development
> **Prerequisites:**  Python 3.8+, Node.js, TypeScript
```bash
cd RBMWeb2 && npm install && npm run build && cd ..
pip install setuptools wheel pyyaml
pip install packages/QFlowLayout packages/QCollapsibleCheckList
pip install -e ".[full]"
```

<!-- ### Docker deployment <span style="color:red">[outdated]</span>
<span style="color:blue">To be revised...</span>   
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
``` -->

## Usage:
**To start the client GUI program:**
```bash
resbibman client
```
The client is a GUI written in PyQt6, it can be used to manage local database, or to connect to the RBM server and work in online mode.

**To start the RBM server and RBMWeb server:**
```bash
resbibman server
```
The RBM and RBMWeb server are Tornado servers,   
- RBM server provides API for the client (GUI & WebUI & CLI) to communicate with.
- RBMWeb server is a frontend server for RBMWeb(2) frontend.

**To start the iRBM server:**
```bash
resbibman iserver
```
The iRBM server is written with FastAPI, it provides additional AI features and is designed to be connected by the RBM server, so that the server can provide AI features to the client.  
> The reason to separate iRBM server from RBM server are the following:
>  AI features may require more resources, so that the iserver can be deployed on a more powerful machine. If the user does not need AI features, there is no need to start the iserver and install the heavy AI dependencies.
>  It is also possible that the iserver needs a proxy to access the internet, while the RBM server does not.  


For CLI help, see `resbibman -h`  


### Configure
`$RBM_HOME` directory is used for application data storage, by default it is set to `~/.RBM`.  
The data directory contains the configuration file, log files, default database, RBMWeb backend data, cache files...  

To start the application with arbitrary data directory, you can run: 
```bash
RBM_HOME="your/path/here" resbibman ...
```

Other management tools include: 

```bash
rbm-keyman      # Manage access key
rbm-discuss     # Manage online discussions
rbm-collect     # Automatic add entry to database with retriving string
rbm-resetconf   # To reset default configuration
rbm-share       # To generate share url
rbm-index       # To build and query feature of the database, for fuzzy search
rbm-utils       # Miscellaneous utilities
```

# Manual and documentations
- [api-usage](resbibman/docs/api.md)


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
- [x] Other citation format convert to bibtex
- [x] Key-user relation, mandatory tags
- [x] Server search
- [x] Related works
- [ ] Reading time
- [ ] Dashboard page
- [ ] Within software cross-reference
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
- [x] Right click: open url, free local

Main window:
- [x] Refresh button

settings:

Tags:
- [x] Right click: rename; delete;
- [x] Sub-tags (Cascading tags / Nested tags)

Refractor:
- [ ] Move more methods into core classes

rbm-collect:
- [ ] web
- [ ] medRxiv
- [ ] bioRxiv
- [ ] PMID

### Long time goals

- [ ] Relation graph
- [ ] ~~Language support~~

<!-- ## Ideas: -->
<!-- QRunnable for multithreading -->
<!--  -->

</details>

## Known issues

<!-- * May crash when changing selection (caused by auto saving) -->
* Markdown horizontal line highlighter not working somehow
* Adding file may encounter permission error for FAT32 format destination in Linux machine (refer to: [stackoverflow-25716333](https://stackoverflow.com/questions/25716333/))
* Add data without tag permission on non-admin account, then delete local will raise exception
* Full-screen GUI in macOS may somehow crash
* ~~QWebEngineView may not show html(not work on opensuse and ubuntu22.04?)~~(Resolved with PyQt6)
* ~~PDFReader based on QWebEngineView may not show PDF (For PyQt6 under Windows, refer to: [stachoverflow-73350761](https://stackoverflow.com/questions/73350761/))~~(Resolved using PDF.js)

<!-- ## Credits:
https://github.com/google/material-design-icons   
https://mozilla.github.io/pdf.js/   -->
<!-- https://github.com/MathJax/MathJax   -->
