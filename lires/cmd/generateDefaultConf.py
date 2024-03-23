from ..config import generateDefaultConf
import argparse

def run():
	parser = argparse.ArgumentParser(description="Generate default configuration file")
	parser.add_argument("-i", "--database_id", type=str, help="Database ID", default=None)
	args = parser.parse_args()
	generateDefaultConf(args.database_id)

if __name__ == "__main__":
	run()