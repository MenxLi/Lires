# Lires 
**A self-hosted research literature manager!**   

The name of Lires is a combination of **Lire** and **Res**earch, where **Lire** is the French word for '***Read***'.

![LiresWeb-GUI](https://limengxun-imagebed.oss-cn-wuhan-lr.aliyuncs.com/liresweb1.1.3v0.png)

Lires is designed to be deployed onto a server to provide a **self-hosted collaborative solution** for research literature management.

The software mainly consists of two modules:  
1. `lires`, the core server, provide APIs for the client
2. `lires-web`, the web client for user interaction
3. `lires-ai`, a stateless AI server for computational intelligence features  

## Features
📚 Shared database  
🔄 Cross-platform  
🏷️ Cascading tags    
📝 Markdown notes  
👥 Multi-user management  
✨ Artificial intelligence

Currently, it supports PDF file and provides above mentioned basic features, such as adding tags, notes, and searching. Some advanced features including semantic search, auto summarization and arxiv subscription are also avaliable.   
**These should be enough for most use cases, more features will be added in the future.**

# Getting started
**Fetch all submodules**
```sh
git submodule update --init --recursive
```

**Docker deployment**
```sh
docker compose up

# register a user and download pdf.js viewer on the first run 
# no need to run again if the container is re-created / re-started
docker exec lrs lrs-user add <username> <password> --admin
docker exec lrs lrs-utils download_pdfjs
```
Now open the browser and visit the WebUI at `http://localhost:8080`.

**Please refer to the documents for more details on [getting started](docs/gettingStarted.md).**

# Manuals and documentations
- [Getting started](docs/gettingStarted.md)
- [Development](docs/devGuide.md)