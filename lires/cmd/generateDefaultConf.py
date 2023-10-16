import os
from ..confReader import CONF_FILE_PATH, saveToConf, DEFAULT_DATA_PATH, DEFAULT_PDF_VIEWER_DIR

def run():
	generateDefaultConf()

	try:
		from lires_qt.config import generateDefaultGUIConfig
		generateDefaultGUIConfig()
	except ModuleNotFoundError:
		print("Failed to import lires_qt.config, skip generating GUI configuration file")

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
