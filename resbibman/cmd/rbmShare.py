"""
To generate share page
"""

import argparse
import urllib.parse
from resbibman.confReader import getConf

def main():
	parser = argparse.ArgumentParser("rbm-share")
	parser.add_argument("-t", "--tags", default=[], nargs="+")

	args = parser.parse_args()
	addr = "http://{}:{}/frontend/index.html".format(getConf()["host"], getConf()["port"])
	
	params = {
		"tags":"&&".join(args.tags)
	}
	aim_addr = "{}?{}".format(addr, urllib.parse.urlencode(params)) 
	print(aim_addr)

if __name__ == "__main__":
	main()

