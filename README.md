# Lires 
**A self-hosted research literature manager!**   

![RBMWeb-GUI](http://limengxun.com/files/imgs/rbmweb.png)

Lires is a combination of **Lire** and **Res**earch, where **Lire** is the French word for 'Read'.

## Modules
Mainly consists of two server modules:  
1. `lires`, the core server
2. `ilires`, AI server for computational intelligence features  

And two frontend modules:  
1. `lires-web` (WebUI)
2. `lires-qt` (Desktop GUI, less maintained)

It is designed to be deployed onto a server to share literatures or work in online mode.

## Features
* Host a server to view, share and discuss online
* Cross-platform
* Cascading tags  
* Markdown notes
* Multi-user permission management
* AI-powered features (iRBM)

# Getting started
**Fetch all submodules**
```sh
git submodule update --init --recursive
```

**Docker deployment**
```sh
# build docker image
docker build -t lires:latest .

# create a conainer and start the servers
docker run -d -p 8080:8080 -p 8081:8081 -v $HOME/.RBM:/root/.RBM --name lrs lires:latest

# register a user and download pdf.js viewer on the first run 
# (no need to run again if the container is re-created / re-started)
docker exec lrs lrs-keyman register <your_key_here> --admin
docker exec lrs lrs-utils download_pdfjs
```
Now open the browser and visit the WebUI on `http://localhost:8081`.

Please refer to the documents for more details on [getting started](docs/gettingStarted.md).

# Manuals and documentations
- [Getting started](docs/gettingStarted.md)
- [API-usage](docs/api.md)
- [Development](docs/devGuide.md)
