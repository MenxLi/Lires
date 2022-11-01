import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Miscellaneous utilities for resbibman.")
    parser.add_argument("task", choices=["download_pdfjs"])

    args = parser.parse_args()

    if args.task == "download_pdfjs":
        from resbibman.core.pdfTools import downloadDefaultPDFjsViewer
        downloadDefaultPDFjsViewer()