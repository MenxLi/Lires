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
Installation:
```sh
pip install 'Lires[all]'
```

Register your first user, the admin user will be able to manage other users using the web interface:
``` sh
lrs-user add <username> <password> --admin
```

Start the servers:
``` sh
lires server    # start the core server
lires iserver   # start the AI server
```

Now open the browser and visit the WebUI at `http://localhost:8080`.

**Please refer to the documents for more details on [getting started](docs/gettingStarted.md)**.

# Manuals and documentations
- [Getting started](docs/gettingStarted.md)
- [Development](docs/devGuide.md)
- [User manual - 中文](docs/userManual_zh/index.html) (WIP...)