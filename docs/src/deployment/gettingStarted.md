# Getting Started

This guide will help you to install and start the Lires server.   
For using it with Docker, please refer to [Docker Deployment](./docker.md).

## Table of Contents
[[toc]]

## Installation

### From PyPI
```bash
pip install 'Lires[all]'
```

### From source
1. Init submodules
```bash 
git submodule update --init --recursive
```
2. Compile frontend files
> **Prerequisites:**  Node.js, Make
```bash
make build
```
3. Install the servers
> **Prerequisites:**  C++17 compiler
```bash
pip install ".[all]"
```

## Server startup

### Manual startup
Start the microservices with the following commands:
```bash
lires registry  # the global resource module, for service discovery
lires log       # the log service
lires ai        # the AI service
lires feed      # the feed service
```
Lires services are designed to be scalable, and can be started with multiple instances (except for the registry service).
::: info
The `registry` service is for service discovery, and should be started before other services.
:::

Then, start the gateway server:
```sh
lires server    # the gateway server
```
Lires server is a tornado server that provides API for the client (WebUI & CLI) to communicate with, and should be exposed to the internet.    

::: details
#### More on starting the servers
`$LRS_HOME` directory is used for application data storage, by default it is set to `~/.Lires`.  
The data directory contains the configuration file, log files, database, cache files...  

To start the application with arbitrary data directory, you can run: 
```bash
LRS_HOME="your/path/here" lires ...
```

Additionally, various environment variables can be set to customize the behavior of the application. 
A detailed list of environment variables can be found at **[here](./enviromentVariables.md)**.
:::

---

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

### Create the first user
**On the first run** you need to create a user account, which can be done by running the `lrs-user` command in the container.
```sh
# export LRS_HOME="..."
lrs-user add <username> <password> --admin
```
For more information, see [User management](./manage.md#user-management).


## Management
There are several management tools for the server, they are all accessible by `lrs-<tool_name>`.  
A list of all the tools and common tasks can be found in [manage.md](./manage.md).