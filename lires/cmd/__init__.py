
try:
    from lires.confReader import getConf
    from tiny_vectordb import VectorCollection

    # as cmd module contains mostly standalone scripts, 
    # set global vector collection compiling config here in case it is used
    VectorCollection.COMPILE_CONFIG = getConf()["tiny_vectordb_compile_config"]

except (FileNotFoundError, KeyError):
    # before configuration is created, or configuration file is outdated
    from lires.core import globalVar as G
    G.logger_lrs.warning("Configuration file not found, or outdated. Please run `lrs-resetconf` to initialize the configuration file")