import argparse

from resbibman.core.pdfTools import DEFAULT_PDFJS_DOWNLOADING_URL

def main():
    parser = argparse.ArgumentParser("Miscellaneous utilities for resbibman.")
    sub_parser = parser.add_subparsers(dest = "subparser", help = "task")

    parser_download_pdfjs = sub_parser.add_parser("download_pdfjs", help="download PDF.js distribution")
    parser_download_pdfjs.add_argument("-u", "--url", help = "downloading url", default=DEFAULT_PDFJS_DOWNLOADING_URL)

    args = parser.parse_args()

    if args.subparser == "download_pdfjs":
        from resbibman.core.pdfTools import downloadDefaultPDFjsViewer
        downloadDefaultPDFjsViewer(download_url=args.url)

if __name__ == "__main__":
    main()