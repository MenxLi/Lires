# Getting Started

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Getting Started](#getting-started)
  - [Installation](#installation)
    - [Server-side manual installation](#server-side-manual-installation)
  - [Server startup](#server-startup)
    - [Basic entries](#basic-entries)
    - [More on starting the servers](#more-on-starting-the-servers)
    - [Cluster startup](#cluster-startup)
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
cd lires_web
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
lrs-utils download_pdfjs                # download pdf.js viewer to serve pdf with the viewer in LiresWeb
```
**[Optional]** Compile tauri GUI
> **Prerequisites:**  Node.js, TypeScript, Rust
```bash
cd lires_web
npm install
npm run app:build
```
---
## Server startup

### Basic entries
**Start the Lires:**
```bash
lires server
```
Lires is a tornado server that provides API for the client (GUI & WebUI & CLI) to communicate with.

**Start the LiresAI:**
```bash
lires iserver
```
The LiresAI server is written with FastAPI, it provides additional AI features and is designed to be connected by the Lires server, so that the latter can provide AI features to the client.  

**Start the LiresWeb:**  
```bash
lires web
```
LiresWeb is a Web-UI frontend.

> <details> 
> <summary>The reason to separate LiresAI server from Lires server</summary>  
> - AI features may require more resources, so that the iserver can be deployed on a more powerful machine. If the user does not need AI features, there is no need to start the iserver and install the heavy AI dependencies.  <br>
> - Allocating resources to the iserver and Lires server separately can be more flexible. For example, the iserver may need more GPU memory, we can launch multiple Lires servers pointing to different `$LRS_HOME`, while sharing the same iserver. <br>
> -  It is also possible that the iserver needs a proxy to access the internet, while the Lires server does not.   
</details>

### More on starting the servers
`$LRS_HOME` directory is used for application data storage, by default it is set to `~/.Lires`.  
The data directory contains the configuration file, log files, default database, LiresWeb backend data, cache files...  

To start the application with arbitrary data directory, you can run: 
```bash
LRS_HOME="your/path/here" lires ...
```
Typically, the lires server can be started by binding a different port to each database and providing services to different users. Which can be achieved by setting the `$LRS_HOME` variable.  

Additionally, SSL certificates can be configured using `$LRS_SSL_CERTFILE` and `$LRS_SSL_KEYFILE` to enable HTTPS 
(we must serve in HTTPS for tauri GUI to connect - [reason](https://github.com/tauri-apps/tauri/issues/2002)).  

Lastly, these servers can share the same 'iServer' for AI features, possibly on a different machine.  

Thus a more general command to start the server is:
```sh
LRS_HOME="your/path/here" LRS_SSL_CERTFILE="your/cert/file" LRS_SSL_KEYFILE="your/key/file" lires server \
    --iserver_host "your/iserver/host" --iserver_port "youriserverport" --port "yourport"
```

The LiresAI server is usually started with OPENAI API keys, which can be set with environment variable:
```sh
OPENAI_API_KEY="sk-xxxx" lires iserver --openai-api-base "https://api.openai.com/v1"
```
Note that openai api base must be set via command line argument (or leave it to default), because it is not a constant in current implementation in order to support custom models such as that from [lmsys](https://github.com/lm-sys/FastChat).

### Cluster startup
It will be laborious and error-prone to start multiple servers manually.  
Especially when we want to start multiple servers with different configurations.  

Instead, we provide a simple script to enable server clustering for easy deployment.  
```sh
# Generate a template configuration file
lrs-cluster <your/configuration.yaml> --generate

# Edit the configuration file
# ...

# Start the cluster
lrs-cluster <your/configuration.yaml>
```
The configuration file designates the environment variables, as well as the command line arguments for each server.

---

## Management
### User management
After installation, user access keys should be generated with `lrs-keyman` command.
```sh
lrs-keyman register <your_key> --admin
```
for more information, see `lrs-keyman -h`.  

### Build search index
The search index is used for **semantic search** and querying **related works**,
It is currently implemented as building feature vectors for each entry (thanks to [huggingface transformers](https://huggingface.co/docs/transformers/index)), 
and use cosine similarity to measure the distance between vectors.

To build the index, run:  
**This requires LiresAI server to be running.**
```sh
lrs-index build
```
*The priority for indexing sources: Abstract > AI summerization > PDF full text*

### All management tools

All managements tools include:
```sh
lrs-cluster     # Cluster management
lrs-keyman      # Manage access key
lrs-discuss     # Manage online discussions
lrs-collect     # Automatic add entry to database with retriving string
lrs-resetconf   # To reset default configuration
lrs-share       # To generate share url
lrs-index       # To build and query feature of the database, for fuzzy search
lrs-utils       # Miscellaneous utilities
```

---
## Docker deployment
Instead of installing the server, you can also deploy the server using docker.  
Which adds additional security and building efficiency.  
```sh
# creates a docker image named lires
docker build -t lires:latest .

# create the container named 'lrs', 
# please change the port mapping and volume mapping as needed
# depending on your need, you may want to expose only a subset of the ports
docker run -d -p 8080:8080 -p 8081:8081 -v $HOME/.Lires:/root/.Lires --name lrs lires:latest
```

The container runs server cluster with configuration at `/root/.Lires/container-cluster-config.yaml` (Which should be mounted to the host).  
You can edit the configuration file to change the server settings.

**To maximize the compatibility, The container image by default does not use GPU for AI features.**  
**It's suggested to disable iserver on the container by modifying the configuration file.**  

Instead, we can set the server settings pointing to the shared LiresAI server outside of the container, maybe on the host machine / another machine with GPU, or on another container.  
> This can be done by delete the `iserver` section in the configuration file.  
> Then, set the `server -> ARGS -> iserver_*` section to point to the LiresAI server.
> 
> For example, if the LiresAI server is running on the host machine with IP address `192.168.3.6:8731`, then we can set the `iserver_host` to `192.168.3.6` and `iserver_port` to `8731`.

**On the first run** you need to generate the user key, which can be done by running the `lrs-keyman` command in the container.
and you also need to download the pdf.js viewer to serve pdf with the viewer in LiresWeb.
The user information and pdf.js viewer will be stored in the volume mapping directory, so that they will not be lost when the container is removed.
```sh
docker exec lrs lrs-keyman register your_key --admin
docker exec lrs lrs-utils download_pdfjs
```

Other management tools can be run in the container.  
```sh
docker exec lrs lrs-...
```

---

## Optional - PyQt6 GUI
There is a PyQt6 GUI, which can be installed on the server for GUI management in offline mode, or on the client as a secondary native GUI.

![lrsgui](http://limengxun.com/files/imgs/rbmgui.png)

**(PyQt GUI are legacy codes.  There will be less mantainance for it in the future.)**

Installation:
```sh
pip install packages/QFlowLayout packages/QCollapsibleCheckList
pip install .[gui]
```

**To start the client GUI program:**
```bash
lires client
```