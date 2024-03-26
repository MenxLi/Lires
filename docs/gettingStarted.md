# Getting Started

<!-- > [!WARNING]  
> This document is for version 1.3.9, needs update.   -->

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Getting Started](#getting-started)
  - [Introduction](#introduction)
    - [Features](#features)
  - [Quick Start](#quick-start)
  - [Manual Deployment](#manual-deployment)
    - [Installation from source](#installation-from-source)
    - [Server startup](#server-startup)
      - [Basic entries](#basic-entries)
      - [More on starting the servers](#more-on-starting-the-servers)
    - [Cluster startup](#cluster-startup)
    - [On the first run](#on-the-first-run)
  - [Management](#management)
    - [User management](#user-management)
    - [Build search index](#build-search-index)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

The name of Lires is a combination of **Lire** and **Res**earch, where **Lire** is the French word for '***Read***'.

![LiresWeb-GUI](https://limengxun-imagebed.oss-cn-wuhan-lr.aliyuncs.com/liresweb1.1.3v0.png)

Lires is designed to be deployed onto a server to provide a **self-hosted collaborative solution** for research literature management.

The software mainly consists of four modules:  
1. `lires`, the global resource module.
2. `lires-server`, the main entry point for the client.
3. `lires-service`, microservices for enhanced scalability. 
4. `lires-web`, a web-based interface for user interaction.

### Features
📚 Shared database  
🔄 Cross-platform  
🏷️ Cascading tags    
📝 Markdown notes  
👥 Multi-user management  
✨ Artificial intelligence  
🚀 Scalable deployment  

## Quick Start

```sh
pip install 'Lires[all]'
lrs-user add <username> <password> --admin
lrs-cluster -i ~/.Lires/cluster-config.toml
```


## Manual Deployment

### Installation from source
Compile frontend files
> **Prerequisites:**  Node.js
```bash
cd lires_web
npm install
npm run build
cd ..
```
Install the servers
> **Prerequisites:**  Python 3.8+, GCC
```bash
pip install ".[all]"
```
---
### Server startup

#### Basic entries
```bash
lires registry  # the global resource module, for service discovery
lires server    # the gateway server
lires log       # the log service
lires ai        # the AI service
lires feed      # the feed service
```
Lires server is a tornado server that provides API for the client (WebUI & CLI) to communicate with, and should be exposed to the internet.    

The whole application is scalable, heavy tasks will be offloaded to services like AI, log, and feed. 
The services running independently and can have multiple instances.
> Note: the `registry` service is for service discovery, and should be started before other services.

#### More on starting the servers
`$LRS_HOME` directory is used for application data storage, by default it is set to `~/.Lires`.  
The data directory contains the configuration file, log files, database, cache files...  

To start the application with arbitrary data directory, you can run: 
```bash
LRS_HOME="your/path/here" lires ...
```

Additionally, various environment variables can be set to customize the behavior of the application. 
A detailed list of environment variables can be found at **[here](./enviromentVariables.md)**.

---

### Cluster startup
It will be laborious and error-prone to start multiple servers manually.  
Especially when we want to start multiple servers with different configurations.  

Instead, we provide a simple script to enable server clustering for easy deployment.  
```sh
# Generate a template configuration file
lrs-cluster <your/configuration.toml> --generate

# Edit the configuration file
# ...

# Start the cluster
lrs-cluster <your/configuration.toml>
```
The configuration file designates the environment variables, as well as the command line arguments for each server.

---

### On the first run
**On the first run** you need to create a user account, which can be done by running the `lrs-user` command in the container.
```sh
# export LRS_HOME="..."
lrs-user add <username> <password> --admin
```
After the user is created, you can manage other users with this user via the web interface.

---

## Management
There are several management tools for the server, they are all accessible by `lrs-<tool_name>`.  
A detailed description of each tool can be found in [manage.md](./manage.md).

Following are some common management tasks.
### User management
After installation, user should be registered with `lrs-user` command.
```sh
lrs-user add <username> <password>
```
Or you want to change the password, admin status, or tag permisson of a user, run:
```sh
lrs-user update <username> -p <password> -t "tag1" "tag2->subtag" --admin true
```
for more information, see `lrs-user -h`.  

### Build search index
The search index is used for **semantic search** and querying **related works**,
It is currently implemented as building feature vectors for each entry (thanks to [huggingface transformers](https://huggingface.co/docs/transformers/index)), 
and use cosine similarity to measure the distance between vectors.

**No need to manually build the index**, the index will be periodically updated by the server.   
If you add a document and want to update the index immediately, or you want to use LLM to summarize all the no-absract entries for indexing, you can run:
```sh
lrs-index build
```
**This requires LiresAI server to be running.**
*The priority for indexing sources: Abstract > AI summerization > PDF full text*
