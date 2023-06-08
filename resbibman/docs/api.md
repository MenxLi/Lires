
# Client-side APIs

`resbibman.api` is a collection of APIs for resbibman client,
It is designed for easy retrieval of most frequently used modules of resbibman

**For example, to retrieve a list of all the papers information:**

From local database:
```python
from resbibman.api import DataBase, getConf
config = getConf()
database = DataBase(config['database'], force_offline = True)
summaries = [data.summary for data in database.values()]
```
From the server:
```python
# the host, port and key should be setup in the config file or through GUI
from resbibman.api import ServerConn
summaries = ServerConn().summaries()
```

More examples can be found in the [api_examples](../../api_examples) folder.