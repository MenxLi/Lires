import os
from ..core.dataClass import DataTableList
from ..confReader import CONF_FILE_PATH, saveToConf, DEFAULT_DATA_PATH, DEFAULT_PDF_VIEWER_DIR

def run():
	generateDefaultConf()

try:
	import darkdetect
	# this is the only place where darkdetect is used, 
	# this dependency is not required for the server environment
	is_sys_darkmode = darkdetect.isDark()
except ImportError:
	is_sys_darkmode = False

def generateDefaultConf():
	"""
	"database" points to local database, used by LiresWeb,
	"""
	saveToConf(
		## CORE SETTINGS ##
		accepted_extensions = [".pdf", ".caj", ".html", ".hpack", ".md", ".pptx", ".ppt"],
		database = DEFAULT_DATA_PATH,

		host = "",
		port = "8080",
		access_key = "",

		pdfjs_viewer_path = os.path.join(DEFAULT_PDF_VIEWER_DIR, "web", "viewer.html"),

		## GUI SETTINGS ##
		# Maybe move them to a separate file?
		server_preset = [{
			"host": "http://localhost",
			"port": "8080",
			"access_key": ""
		}],

		default_tags = [],
		table_headers = [ 
				DataTableList.HEADER_FILESTATUS,
				DataTableList.HEADER_TITLE,
				DataTableList.HEADER_YEAR, 
				DataTableList.HEADER_AUTHOR
			 ],
		sort_method = DataTableList.SORT_TIMEADDED,
		sort_reverse = False,
		font_sizes = {
			"data": ["Arial", 10],
			"tag": ["Arial", 10]

		},
        stylesheet = "Simple-dark" if is_sys_darkmode else "Simple",
		auto_save_comments = False,
		gui_status = {
			"show_toolbar": True,
			"tag_uncollapsed": []
		},
		proxies = {
			"proxy_config": {
				"proxy_type": "socks5",
				"host": "127.0.0.1",
				"port": ""
			},
			"enable_requests": False,
			"enable_qt": False,
		},

    )
	print("Generated default configuration file at: ", CONF_FILE_PATH)

if __name__ == "__main__":
	run()
