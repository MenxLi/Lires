
import tempfile, os

from lires.confReader import LRS_HOME
from lires.cmd.cluster import generateConfigFile, loadConfigFile


tempdir = tempfile.TemporaryDirectory()

# config_file = os.path.join(tempdir.name, "lrs_cluster.yaml")
config_file = os.path.join(LRS_HOME, "lrs_cluster.yaml")
print(config_file)
generateConfigFile(config_file)

loadConfigFile(config_file)