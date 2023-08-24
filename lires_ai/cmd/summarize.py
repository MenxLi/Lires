import asyncio
import argparse
try:
    from lires.core.pdfTools import PDFAnalyser
except ImportError:
    raise ImportError("Please install Lires[core] first")
from ..lmTools import summarize, structuredSummerize, featurize
from ..lmInterface import streamOutput

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('pdf_path', type=str, help='path to pdf file')
    parser.add_argument('--structured', action='store_true', help='structured summarization')
    parser.add_argument('--model', type=str, default="gpt-3.5-turbo", help='model name')
    parser.add_argument("--max-length", type=int, default=-1, help="max length of the input text, the rest will be truncated")

    args = parser.parse_args()
    with PDFAnalyser(args.pdf_path) as doc:
        pdf_text = doc.getText()

    max_len = args.max_length
    if max_len == -1: max_len = len(pdf_text.split())
    if len(pdf_text.split()) > max_len: 
        txt = " ".join(pdf_text.split()[:max_len])
    else: txt = pdf_text

    # vec = asyncio.run(featurize(txt, verbose=True))
    # print(vec.shape)
    # exit()

    if args.structured:
        res = asyncio.run(structuredSummerize(txt, print_func=print, model=args.model))
        vec = asyncio.run(featurize(res))
        print("Get vectorized result: ", vec.shape)
    else:
        streamOutput(summarize(txt))

        

if __name__ == "__main__":
    main()