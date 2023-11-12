"""
To generate share page
"""

import argparse
import urllib.parse
from lires.confReader import getConf

def main():
	parser = argparse.ArgumentParser("lrs-share")
	parser.add_argument("-t", "--tags", default=[], nargs="+")

	args = parser.parse_args()
	# TODO: to set front-end address in some way
	addr = ""
	
	params = {
		"tags":"&&".join(args.tags)
	}
	aim_addr = "{}/#/?{}".format(addr, urllib.parse.urlencode(params)) 
	print(aim_addr)

if __name__ == "__main__":
	main()

