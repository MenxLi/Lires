
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
lrs-reset       # To reset default configuration
lrs-index       # To build and query feature of the database, for fuzzy search
lrs-utils       # Miscellaneous utilities (e.g. update pdf.js and edit configuration file)
```

The tools are self-explanatory by name, 
all the tools are written with `argparse` and have a help message that can be accessed by `lrs-<tool_name> -h`.