
# Client-side APIs

`lires.api` is a collection of APIs for lires client,
It is designed for easy retrieval of most frequently used modules of lires

**For example, to retrieve a list of all the papers information:**

From local database:
```python
from lires.api import DataBase, DATABASE_PATH
database = DataBase(DATABASE_PATH)
summaries = [data.summary for data in database.values()]
```
From the server:
```python
# the host, port and key should be setup in the config file or through GUI
from lires.api import ServerConn
summaries = ServerConn().summaries()
```

More examples can be found in the [api_examples](../api_examples) folder.