# Lires 
**A self-hosted research literature manager!**   

The name of Lires is a combination of **Lire** and **Res**earch, where **Lire** is the French word for '***Read***'.

<!-- ![LiresWeb-GUI](http://limengxun.com/files/imgs/rbmweb.png) -->

## Modules
Mainly consists of three modules:  
1. `lires`, the core server
2. `lires-ai`, AI server for computational intelligence features  
3. `lires-web`, the WebUI

It is designed to be deployed onto a server to share literatures or work in online mode.

## Features
* Host a server to view, share and discuss online
* Cross-platform
* Cascading tags  
* Markdown notes
* Multi-user permission management
* AI-powered features (LiresAI)

# Getting started
**Fetch all submodules**
```sh
git submodule update --init --recursive
```

**Docker deployment**
```sh
docker compose up

# register a user and download pdf.js viewer on the first run 
# (no need to run again if the container is re-created / re-started)
docker exec lrs lrs-keyman register <your_key_here> --admin
docker exec lrs lrs-utils download_pdfjs
```
Now open the browser and visit the WebUI on `http://localhost:8081`.

**Please refer to the documents for more details on [getting started](docs/gettingStarted.md).**

# Manuals and documentations
- [Getting started](docs/gettingStarted.md)
- [API-usage](docs/api.md)
- [Development](docs/devGuide.md)
