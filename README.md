# Resbibman 
Resbibman: a **Res**earch **bib**liograpy **man**ager

![RBMWeb-GUI](http://limengxun.com/files/imgs/rbmweb.png)

**A self-hosted research literature manager!**   
<!-- It relies on tags to differentiate papers, and use markdown for notes. -->

## Modules
Mainly consists of two server modules:  
1. resbibman-server (RBM server)
2. iRBM server for computational intelligence features  

And two frontend modules:  
1. RBMWeb (WebUI)
2. Qt client (Desktop GUI, less maintained)

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
docker build -t resbibman:latest .

# create a conainer and start the servers
docker run -d -p 8080:8080 -p 8081:8081 -v $HOME/.RBM:/root/.RBM --name rbm resbibman:latest

# register a user and download pdf.js viewer on the first run 
# (no need to run again if the container is re-created / re-started)
docker exec rbm rbm-keyman register <your_key_here> --admin
docker exec rbm rbm-utils download_pdfjs
```
Now open the browser and visit the WebUI on `http://localhost:8081`.

Please refer to the documents for more details on [getting started](docs/gettingStarted.md).

# Manuals and documentations
- [Getting started](docs/gettingStarted.md)
- [API-usage](docs/api.md)
- [Development](docs/devGuide.md)
