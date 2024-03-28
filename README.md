**Lires - A self-hosted research literature manager.**

![](https://limengxun-imagebed.oss-cn-wuhan-lr.aliyuncs.com/pic/lires_v1.7.3w.png)


Installation:  
```bash
pip install 'Lires[all]'
```

Start the services:  
```bash
lires registry  # Registry server, for service discovery
lires log       # Log server, collect logs from other servers
lires ai        # AI server, offload heavy computation tasks
lires feed      # Feed server, collect feeds
```

Start the main server:  
```bash
lires server    # Main server, the gateway server
```

Then add a user with:  
```bash
lrs-user add <username> <password>  --admin # Add a user
```

Now you can visit the web UI at `http://localhost:8080` and login with the user you just added.  
For more information, please visit the [getting started](./docs/src/deployment/gettingStarted.md#getting-started) document.
