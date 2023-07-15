# Resbibman 
Resbibman: a **Res**earch **bib**liograpy **man**ager

<!--![ResBibMan](./resbibman/docs/imgs/ResBibMan.png)-->
<!--![ResBibMan](./resbibman/docs/imgs/mainWindow.png)-->
![RBMWeb-GUI](http://limengxun.com/files/imgs/resbibman2.png)
A research literature manager that utilize Bibtex file to record paper information, 
it relies on tags to differentiate papers, and use markdown for notes.

It mainly consists of two server modules: resbibman-server (RBM server) with a web viewer (RBMWeb), and iRBM. 
It is designed to be deployed onto a server to share literatures or work in online mode.

## Features
* Host a server to view, share and discuss online
* Cross-platform
* Cascading tags  
* Markdown notes
* Multi-user permission management
* AI-powered features (iRBM)

# Getting started
**Docker deployment**
```sh
# build docker image
docker build -t resbibman .

# create a conainer and start the servers
docker run -d -p 8080:8080 -p 8081:8081 -p 8731:8731 -v $HOME/.RBM:/root/.RBM --name rbm resbibman
# start the iRBM server for AI features (optional)
docker exec -d rbm resbibman iserver

# register a user and download pdf.js viewer on the first run 
# (no need to run again if the container is re-created)
docker exec rbm rbm-keyman register <your_key_here> --admin
docker exec rbm rbm-utils download_pdfjs
```
Now open the browser and visit `http://localhost:8081` to view the web viewer.

Please refer to the documents for more details on [getting started](resbibman/docs/gettingStarted.md).

# Manuals and documentations
- [Getting started](resbibman/docs/gettingStarted.md)
- [API-usage](resbibman/docs/api.md)
- [Development](resbibman/docs/devGuide.md)
