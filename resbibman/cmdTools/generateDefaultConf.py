import json

from ..backend.dataClass import DataList, DataTableList
from ..confReader import CONF_FILE_PATH, saveToConf, DEFAULT_DATA_PATH

def run():
	saveToConf(
		accepted_extensions = [".pdf", ".caj"],
		database = DEFAULT_DATA_PATH,
		default_tags = [],
		sort_method = DataList.SORT_TIMEADDED,
		table_headers = [ 
				DataTableList.HEADER_TITLE,
				DataTableList.HEADER_YEAR, 
				DataTableList.HEADER_AUTHOR
			 ],
		stylesheet = "<None>"
	)

if __name__ == "__main__":
	run()