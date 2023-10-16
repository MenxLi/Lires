import os
from ..confReader import generateDefaultConf

def run():
	generateDefaultConf()

	try:
		from lires_qt.config import generateDefaultGUIConfig
		generateDefaultGUIConfig()
	except ModuleNotFoundError as e:
		print(e)
		print("Failed to import lires_qt.config, skip generating GUI configuration file")

if __name__ == "__main__":
	run()
