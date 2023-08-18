# Getting Started

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Getting Started](#getting-started)
  - [Installation](#installation)
    - [Server-side manual installation](#server-side-manual-installation)
  - [Server startup](#server-startup)
    - [More on starting the servers](#more-on-starting-the-servers)
  - [Management](#management)
    - [User management](#user-management)
    - [Build search index](#build-search-index)
    - [All management tools](#all-management-tools)
  - [Docker deployment](#docker-deployment)
  - [Optional - PyQt6 GUI](#optional---pyqt6-gui)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->



## Installation

### Server-side manual installation
Compile frontend files
> **Prerequisites:**  Node.js, TypeScript
```bash
cd rbmweb
npm install
npm run build
cd ..
```
Install the server
> **Prerequisites:**  Python 3.8+
```bash
git submodule update --init --recursive
pip install ./packages/tiny_vectordb
pip install ".[ai]"
rbm-utils download_pdfjs                # download pdf.js viewer to serve pdf with the viewer in RBMWeb
```
**[Optional]** Compile tauri GUI
> **Prerequisites:**  Node.js, TypeScript, Rust
```bash
cd rbmweb
npm install
npm run app:build
```
---
## Server startup
**To start the RBM and RBMWeb servers:**
```bash
resbibman server
```
The RBM and RBMWeb are Tornado servers,   
- RBM provides API for the client (GUI & WebUI & CLI) to communicate with.
- RBMWeb is a Web-UI frontend server.

**To start the iRBM server:**
```bash
resbibman iserver
```
The iRBM server is written with FastAPI, it provides additional AI features and is designed to be connected by the RBM server, so that the latter can provide AI features to the client.  

> <details> 
> <summary>The reason to separate iRBM server from RBM server</summary>  
> - AI features may require more resources, so that the iserver can be deployed on a more powerful machine. If the user does not need AI features, there is no need to start the iserver and install the heavy AI dependencies.  <br>
> - Allocating resources to the iserver and RBM server separately can be more flexible. For example, the iserver may need more GPU memory, we can launch multiple RBM servers pointing to different `$RBM_HOME`, while sharing the same iserver. <br>
> -  It is also possible that the iserver needs a proxy to access the internet, while the RBM server does not.   
</details>

### More on starting the servers
`$RBM_HOME` directory is used for application data storage, by default it is set to `~/.RBM`.  
The data directory contains the configuration file, log files, default database, RBMWeb backend data, cache files...  

To start the application with arbitrary data directory, you can run: 
```bash
RBM_HOME="your/path/here" resbibman ...
```
Typically, the ResBibMan server can be started by binding a different port to each database and providing services to different users. Which can be achieved by setting the `$RBM_HOME` variable.  

Additionally, SSL certificates can be configured using `$RBM_SSL_CERTFILE` and `$RBM_SSL_KEYFILE` to enable HTTPS 
(we must serve in HTTPS for tauri GUI to connect - [reason](https://github.com/tauri-apps/tauri/issues/2002)).  

Lastly, these servers can share the same 'iServer' for AI features, possibly on a different machine.  

Thus a more general command to start the server is:
```sh
RBM_HOME="your/path/here" RBM_SSL_CERTFILE="your/cert/file" RBM_SSL_KEYFILE="your/key/file" resbibman server \
    --iserver_host "your/iserver/host" --iserver_port "youriserverport" --port "yourport"
```

The iRBM server is usually started with OPENAI API keys, which can be set with environment variable:
```sh
OPENAI_API_KEY="sk-xxxx" resbibman iserver --openai-api-base "https://api.openai.com/v1"
```
Note that openai api base must be set via command line argument (or leave it to default), because it is not a constant in current implementation in order to support custom models such as that from [lmsys](https://github.com/lm-sys/FastChat).

---

## Management
### User management
After installation, user access keys should be generated with `rbm-keyman` command.
```sh
rbm-keyman register <your_key> --admin
```
for more information, see `rbm-keyman -h`.  

### Build search index
The search index is used for **fuzzy search** and querying **related works**,
It is currently implemented as building feature vectors for each entry (thanks to [huggingface transformers](https://huggingface.co/docs/transformers/index)), 
and use cosine similarity to measure the distance between vectors.

To build the index, run:  
**This requires iRBM server to be running.**
```sh
rbm-index build
```
*The priority for indexing sources: Abstract > AI summerization > PDF full text*

### All management tools

All managements tools include:
```sh
rbm-keyman      # Manage access key
rbm-discuss     # Manage online discussions
rbm-collect     # Automatic add entry to database with retriving string
rbm-resetconf   # To reset default configuration
rbm-share       # To generate share url
rbm-index       # To build and query feature of the database, for fuzzy search
rbm-utils       # Miscellaneous utilities
```

---
## Docker deployment
Instead of installing the server, you can also deploy the server using docker.  
Which adds additional security and building efficiency.  
```sh
# creates a docker image named resbibman
docker build -t resbibman:latest .

# create the container named 'rbm', 
# please change the port mapping and volume mapping as needed
# depending on your need, you may want to expose only a subset of the ports
docker run -d -p 8080:8080 -p 8081:8081 -p 8731:8731 -v $HOME/.RBM:/root/.RBM --name rbm resbibman:latest
```

The container's default entry only starts the RBM and RBMWeb servers, the iRBM server should be started separately, if desired.   
```sh
docker exec -d rbm resbibman iserver
# or running with interactive tty
# docker exec -it rbm resbibman iserver
```

Otherwise, we can set the iserver settings pointing the shared iRBM server, maybe on the host machine / another machine with GPU, or on another container  
For an example, to setup the iserver to local machine of ip address `192.168.3.6` on creating the container, run:
```sh
docker run <... your settings ...> resbibman:latest --iserver_host '192.168.3.6' --iserver_port <...>
```

**On the first run** you need to generate the user key, which can be done by running the `rbm-keyman` command in the container.
and you also need to download the pdf.js viewer to serve pdf with the viewer in RBMWeb.
The user information and pdf.js viewer will be stored in the volume mapping directory, so that they will not be lost when the container is removed.
```sh
docker exec rbm rbm-keyman register your_key --admin
docker exec rbm rbm-utils download_pdfjs
```

Other management tools can be run in the container.  
```sh
docker exec rbm rbm-...
```

---

## Optional - PyQt6 GUI
There is a PyQt6 GUI, which can be installed on the server for GUI management in offline mode, or on the client as a secondary native GUI.

![rbmgui](http://limengxun.com/files/imgs/rbmgui.png)

**(PyQt GUI are legacy codes.  There will be less mantainance for it in the future.)**

Installation:
```sh
pip install packages/QFlowLayout packages/QCollapsibleCheckList
pip install .[gui]
```

**To start the client GUI program:**
```bash
resbibman client
```