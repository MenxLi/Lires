
# Server Management Tools

There are several management tools for the server, they are all accessible by `lrs-<tool_name>`.  

All managements tools include:
```sh
lrs-cluster     # Cluster management
lrs-status      # To check the status of the program
lrs-invite      # Manage invitation codes
lrs-user        # Manage user accounts
lrs-log         # Check and view logs
lrs-clear       # Clear data files
lrs-config      # Check, edit, and reset configuration
lrs-index       # To build and query feature of the database, for fuzzy search
lrs-utils       # Miscellaneous utilities (e.g. update pdf.js)
```

**The tools are self-explanatory by name, all the tools are written with `argparse` and have a help message that can be accessed by `lrs-<tool_name> -h`.**

*Following are some common management tasks.*

## User management
After installation, user should be registered with `lrs-user` command.
```sh
lrs-user add <username> <password>
```
Or you want to change the password, or admin status of a user, run:
```sh
lrs-user update <username> -p <password> --admin true
```
You can check current user information with:
```sh
lrs-user list -t
```

### Invitation code
In addition, the user is allowed to register from the web interface with an invitation code. 
The invitation code can be managed by `lrs-invite` command.
```sh
lrs-invite create <code> -m <max_use>
```


## Log management
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

::: warning
Log archiving should be done when the log server is not running, 
otherwise, the log server will try to write to the removed files and cause errors.
:::
