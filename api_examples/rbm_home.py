"""
LRS_HOME is a environment variable which is the path to the root of the lires data
you can refer to lires.confReader.py for more details.

This script shows how to use the environment variable LRS_HOME to create a temporary data folder for your project.
"""

import os, tempfile, shutil, subprocess
from pprint import pprint
# create a new temporary folder and it's path
tempdir = tempfile.mkdtemp()

# set the environment variable LRS_HOME
os.environ['LRS_HOME'] = tempdir

# call subprocess to create a default lires config
# don't forget to copy the environment variables!
subprocess.check_call(['rbm-resetconf'], env=os.environ.copy())

# now import the lires modules to do experiments in the temporary data folder!
# experiments: set configuration host and port
from lires.api import LRS_HOME, getConf, saveToConf
print("LRS_HOME: ", LRS_HOME)

config = getConf()
config["host"] = "127.0.0.1"
config["port"] = "55231"
saveToConf(**config)

new_config = getConf()  # load the new configuration
pprint(new_config)

# clean up
shutil.rmtree(tempdir)