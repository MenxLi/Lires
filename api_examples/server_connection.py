
from pprint import pprint
from resbibman.core.dataClass import DataBase
from resbibman.confReader import getDatabase
from resbibman.initLogger import initLogger

logger = initLogger("DEBUG")

# the data will be stored in a separate database when online mode is used
# you can use any database path you want
tmp_db_path = getDatabase(offline=False) 

## server information should be setup in the config file
database = DataBase().init(tmp_db_path)

all_uids = database.keys()
uid = next(iter(all_uids))

dp = database[uid]

# datapoint is not syncronized to local by default
print("Data is syncronized to local: ", "yes" if dp.is_local else "no")
# syncronize datapoint to local
dp.sync()
# now datapoint is syncronized to local
print("Data is syncronized to local: ", "yes" if dp.is_local else "no")

# now change the data's comment
old_comments = dp.fm.readComments()
dp.fm.writeComments(f"{old_comments}\nThis is a new comment!")

# update all data's information to be the same as the remote data
# database.fetch()      # not need for this example, since we have just syncronized the data

# syncronize datapoint again will compare the local data and remote data's timestamp
# if the local data is newer, the local data will be uploaded to the server
dp.sync()

pprint(dp.fm.readComments())

# it's save to delete the temporary database now
import shutil
assert tmp_db_path == getDatabase(offline=False) # make sure don't accidentally delete the wrong path
database.conn.close()
shutil.rmtree(tmp_db_path)