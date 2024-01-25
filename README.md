# Lires 
**A self-hosted research literature manager!**   

The name of Lires is a combination of **Lire** and **Res**earch, where **Lire** is the French word for '***Read***'.

![LiresWeb-GUI](https://limengxun-imagebed.oss-cn-wuhan-lr.aliyuncs.com/liresweb1.1.3v0.png)

Lires is designed to be deployed onto a server to provide a **self-hosted collaborative solution** for research literature management.

The software mainly consists of four modules:  
1. `lires`, the global resource module.
2. `lires-server`, the main entry point for the client.
3. `lires-service`, microservices for enhanced scalability. 
4. `lires-web`, a web-based interface for user interaction.

## Features
📚 Shared database  
🔄 Cross-platform  
🏷️ Cascading tags    
📝 Markdown notes  
👥 Multi-user management  
✨ Artificial intelligence  
🚀 Scalable deployment  

# Getting started
Installation:
```sh
pip install 'Lires[all]'
```

Register your first user, the admin user will be able to manage other users using the web interface:
``` sh
lrs-user add <username> <password> --admin
```

Start the servers with cluter manager
```sh
lrs-cluster -i ./config.yaml
```

Now open the browser and visit the WebUI at `http://localhost:8080`.

**Please refer to the documents for more details on [getting started](docs/gettingStarted.md)**.

# Manuals and documentations
- [Getting started](docs/gettingStarted.md)
- [Development](docs/devGuide.md)
- [User manual - 中文](docs/userManual_zh/index.html) (WIP...)