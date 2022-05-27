from ..core.dataClass import DataList, DataTableList
from ..confReader import CONF_FILE_PATH, saveToConf, DEFAULT_DATA_PATH

def run():
	generateDefaultConf()

def generateDefaultConf():
	"""
	"database" points to local database, used by RBMWeb,
	"""
	saveToConf(
		accepted_extensions = [".pdf", ".caj", ".html", ".hpack", ".md", ".pptx", ".ppt"],
		database = DEFAULT_DATA_PATH,
		host = "",
		port = "8080",
		access_key = "",
		default_tags = [],
		sort_method = DataTableList.SORT_TIMEADDED,
		table_headers = [ 
				DataTableList.HEADER_FILESTATUS,
				DataTableList.HEADER_TITLE,
				DataTableList.HEADER_YEAR, 
				DataTableList.HEADER_AUTHOR
			 ],
		auto_save_comments = False,
        stylesheet = "Simple"
    )
	print("Generated default configuration file at: ", CONF_FILE_PATH)

if __name__ == "__main__":
	run()
