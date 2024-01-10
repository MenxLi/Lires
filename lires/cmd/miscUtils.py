import argparse

from lires.core.pdfTools import DEFAULT_PDFJS_DOWNLOADING_URL

def main():
    parser = argparse.ArgumentParser("Miscellaneous utilities for lires.")
    sub_parser = parser.add_subparsers(dest = "subparser", help = "task")

    parser_update_pdfjs = sub_parser.add_parser("update_pdfjs", help="update PDF.js distribution")
    parser_update_pdfjs.add_argument("-u", "--url", help = "downloading url", default=DEFAULT_PDFJS_DOWNLOADING_URL)

    parser_edit_config = sub_parser.add_parser("edit_config", help="edit configuration file")
    parser_edit_config.add_argument("-u", "--use_editor", default="", help="choose editor, e.g. . -u vim will invoke 'vim <config>.json'")

    args = parser.parse_args()

    if args.subparser == "update_pdfjs":
        from lires_server.config import PDF_VIEWER_DIR
        from lires.core.pdfTools import downloadDefaultPDFjsViewer
        downloadDefaultPDFjsViewer(download_url=args.url, dst_dir=PDF_VIEWER_DIR, force=True)
    if args.subparser == "edit_config":
        from lires.confReader import CONF_FILE_PATH
        from lires.utils import openFile
        import subprocess
        if args.use_editor:
            subprocess.call([args.use_editor, CONF_FILE_PATH])
        else:
            openFile(CONF_FILE_PATH)


if __name__ == "__main__":
    main()
