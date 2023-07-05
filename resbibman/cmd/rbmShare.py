"""
To generate share page
"""

import argparse
import urllib.parse
from resbibman.confReader import getConf

def main():
	raise DeprecationWarning("This script needs update, may be implemented in the future.")
	parser = argparse.ArgumentParser("rbm-share")
	parser.add_argument("-t", "--tags", default=[], nargs="+")
	parser.add_argument("-p", "--port", default="8081", help="port of the rbmweb frontend")

	args = parser.parse_args()
	# addr = "http://{}:{}/frontend/index.html".format(getConf()["host"], getConf()["port"])
	addr = "http://{}:{}".format(getConf()["host"], args.port)
	
	params = {
		"tags":"&&".join(args.tags)
	}
	aim_addr = "{}?{}".format(addr, urllib.parse.urlencode(params)) 
	print(aim_addr)

if __name__ == "__main__":
	main()

