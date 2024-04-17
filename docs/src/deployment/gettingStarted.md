# Getting Started

<!-- > [!WARNING]  
> This document is for version 1.3.9, needs update.   -->

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Getting Started](#getting-started)
  - [Installation](#installation)
    - [From PyPI](#from-pypi)
    - [From source](#from-source)
  - [Server startup](#server-startup)
      - [Basic entries](#basic-entries)
      - [More on starting the servers](#more-on-starting-the-servers)
    - [Cluster startup](#cluster-startup)
    - [Run with Docker](#run-with-docker)
    - [On the first run](#on-the-first-run)
  - [Management](#management)
    - [User management](#user-management)
    - [Log management](#log-management)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


## Installation

### From PyPI
```bash
pip install 'Lires[all]'
```

### From source
Compile frontend files
> **Prerequisites:**  Node.js, Make
```bash
make build
```
Install the servers
> **Prerequisites:**  Python 3.8+, GCC
```bash
pip install ".[all]"
```

## Server startup
#### Basic entries
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
lrs-cluster <your/configuration.toml> --generate

# Edit the configuration file
# ...

# Start the cluster
lrs-cluster <your/configuration.toml>
```
The configuration file designates the environment variables, as well as the command line arguments for each server.

### Run with Docker
```sh
# build the image
docker build -f docker/Dockerfile -t lires:runtime .

# run the container
docker run -d -p 8080:8080 -v </path/to/data>:/root/.Lires --name lrs lires:runtime

# user management
docker exec -it lrs lrs-user ...

# check the logs
docker exec -it lrs lrs-log ...

# or check output by docker logs
docker logs -f lrs
```

---

### On the first run
**On the first run** you need to create a user account, which can be done by running the `lrs-user` command in the container.
```sh
# export LRS_HOME="..."
lrs-user add <username> <password> --admin
```
After the user is created, you can manage other users with this user via the web interface.


## Management
There are several management tools for the server, they are all accessible by `lrs-<tool_name>`.  
A detailed description of each tool can be found in [manage.md](./manage.md).

**Following are some common management tasks.**

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

### Log management
The log service is used to store the logs of the application, 
the log server can have multiple instances, each one will store the logs in a separate sqlite database.

The logs can be accessed by `lrs-log` command, the output is combined from the results of all log servers.
```sh
lrs-log check
```
This will check the overall logged information, specifically the table names and the number of logs in each table.

To view the log, run:
```sh
lrs-log view -t <table_name> | less
```

Since every startup of the log server will create a new log file, it is recommended to periodically archive the logs.
```sh
lrs-log merge --rm
```
This will merge all the log files into a single file, and remove the original files.
