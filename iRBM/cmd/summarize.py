import asyncio
import argparse
from resbibman.core.pdfTools import PDFAnalyser
from ..lmTools import summarize, structuredSummerize
from ..lmInterface import streamOutput


def getAbstract(content: str) -> str:
    ...

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('pdf_path', type=str, help='path to pdf file')
    parser.add_argument('--structured', action='store_true', help='structured summarization')

    args = parser.parse_args()
    with PDFAnalyser(args.pdf_path) as doc:
        pdf_text = doc.getText()

    max_len = 9
    if len(pdf_text.split()) > max_len: 
        txt = " ".join(pdf_text.split()[:max_len])
    else: txt = pdf_text

    from ..lmTools import vectorize

    if args.structured:
        res = asyncio.run(structuredSummerize(txt, print_func=print))
        vec = asyncio.run(vectorize(res))
        print("Get vectorized result: ", vec.shape)
    else:
        streamOutput(summarize(txt))

        

if __name__ == "__main__":
    main()