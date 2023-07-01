
# Getting Started

## Installation

installation for server
> **Prerequisites:**  Python 3.8+
```bash
pip install setuptools wheel pyyaml
pip install packages/QFlowLayout packages/QCollapsibleCheckList
pip install -e ".[full]"
rbm-utils download_pdfjs                # download pdf.js viewer to serve pdf with the viewer in RBMWeb
```
Compile the frontend
> **Prerequisites:**  Node.js, TypeScript
```bash
cd RBMWeb2
npm install
npm run build
```
Compile the tauri GUI
> **Prerequisites:**  Node.js, TypeScript, Rust
```bash
cd RBMWeb2
npm install
npm run app:build
```

## Server startup
```bash
resbibman server
```
The RBM and RBMWeb server are Tornado servers,   
- RBM server provides API for the client (GUI & WebUI & CLI) to communicate with.
- RBMWeb server is a frontend server for RBMWeb(2) frontend.

Typically, the ResBibMan server can be started by binding a different port to each database and providing services to different users. This can be achieved by setting the `$RBM_HOME` variable.  
Additionally, SSL certificates can be configured using `$RBM_SSL_CERTFILE` and `$RBM_SSL_KEYFILE` to enable HTTPS 
(we must serve in HTTPS for tauri GUI to connect - [reason](https://github.com/tauri-apps/tauri/issues/2002)).  
Meanwhile, these servers can share the same 'iServer' for AI features, possibly on a different machine.  

Thus a more general command to start the server is:
```bash
RBM_HOME="your/path/here" RBM_SSL_CERTFILE="your/cert/file" RBM_SSL_KEYFILE="your/key/file" resbibman server \
    --iserver_host "your/iserver/host" --iserver_port "youriserverport" --port "yourport"
```


## Optional - PyQt6 GUI
There is a PyQt6 GUI as well, it can be installed on the server for GUI management in offline mode, or on the client for online mode.  
(There will be less mantainance for this GUI in the future.)

<!-- > **Prerequisites:**  Python 3.8+
```bash
pip install setuptools wheel pyyaml
pip install packages/QFlowLayout packages/QCollapsibleCheckList
pip install .
rbm-utils download_pdfjs                # [optional] download pdf.js viewer to view pdf inside resbibman
# pip install ".[ai]"                   # [optional] to install with AI dependencies
``` -->
**To start the client GUI program:**
```bash
resbibman client
```
The client is a GUI written in PyQt6, it can be used to manage local database, or to connect to the RBM server and work in online mode.
