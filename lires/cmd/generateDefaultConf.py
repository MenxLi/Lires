from ..config import generateDefaultConf
import argparse

def run():
	parser = argparse.ArgumentParser(description="Generate default configuration file")
	parser.add_argument("-g", "--group", type=str, help="Server ID", default=None)
	args = parser.parse_args()
	generateDefaultConf(args.group)

if __name__ == "__main__":
	run()