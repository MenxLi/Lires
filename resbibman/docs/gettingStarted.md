
# Getting Started

## Installation

### Server-side installation
Compile frontend files
> **Prerequisites:**  Node.js, TypeScript
```bash
cd RBMWeb2
npm install
npm run build
cd ..
```
Install the server
> **Prerequisites:**  Python 3.8+
```bash
pip install ".[ai]"
rbm-utils download_pdfjs                # download pdf.js viewer to serve pdf with the viewer in RBMWeb
```
**[Optional]** Compile tauri GUI
> **Prerequisites:**  Node.js, TypeScript, Rust
```bash
cd RBMWeb2
npm install
npm run app:build
```

### User management
After installation, user access keys should be generated with `rbm-keyman` command.
```sh
rbm-keyman -r your_key --admin
```
for more information, see `rbm-keyman -h`.

---
## Server startup
```sh
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
```sh
RBM_HOME="your/path/here" RBM_SSL_CERTFILE="your/cert/file" RBM_SSL_KEYFILE="your/key/file" resbibman server \
    --iserver_host "your/iserver/host" --iserver_port "youriserverport" --port "yourport"
```

In addition, iRBM server should be started to provide AI services.  
```sh
resbibman iserver
```

## Optional - PyQt6 GUI
There is a PyQt6 GUI, which can be installed on the server for GUI management in offline mode, or on the client as a secondary native GUI.
**(PyQt GUI are legacy codes, it is not recommended to use it.  There will be less mantainance for it in the future.)**

Installation:
```sh
pip install packages/QFlowLayout packages/QCollapsibleCheckList
pip install .[gui]
```

**To start the client GUI program:**
```bash
resbibman client
```