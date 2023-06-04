from ._base import *
import string, os, time
from resbibman.core.serverConn import IServerConn
from resbibman.core.pdfTools import getPDFText
from resbibman.confReader import ASSETS_PATH, DOC_SUMMARY_DIR


class SummaryHandler(tornado.web.RequestHandler, RequestHandlerBase):

    @property
    def summary_html_template(self):
        with open(os.path.join(ASSETS_PATH, "summary.template.html"), "r") as fp:
            _summary_html_template = fp.read()
        return _summary_html_template

    def get(self, uuid):
        return self.write(self.summary_html_template)

class SummaryPostHandler(tornado.web.RequestHandler, RequestHandlerBase):
    def post(self):
        # Set the appropriate headers to enable streaming
        self.set_header('Content-Type', 'text/plain')
        # self.set_header('Transfer-Encoding', 'chunked')
        self.set_header('Cache-Control', 'no-cache')

        uuid = self.get_argument("uuid")
        force = self.get_argument("force", "false").lower() == "true"

        iconn = IServerConn()
        istatus = iconn.status
        if not (istatus and istatus['status']):
            self.write("ERROR: iRBM server not running.")
            return
        
        if not uuid in self.db:
            self.write("ERROR: No such paper.")
            return
        
        dp = self.db[uuid]
        if not (dp.file_path and dp.fm.file_extension == ".pdf"):
            self.write("ERROR: No pdf file.")
            return
        
        # a cache for summary
        summary_txt_path = os.path.join(DOC_SUMMARY_DIR, uuid + ".txt")
        if os.path.exists(summary_txt_path) and not force:
            with open(summary_txt_path, "r") as fp:
                for line in fp.readlines():
                    self.write(line)
                    self.flush()
            return
        
        assert dp.file_path
        # __max_words = 768
        __max_words = 2048
        pdf_txt = getPDFText(dp.file_path, __max_words)

        summary_txt = ""
        res = iconn.chat(
            conv_dict={
                "system": "A conversation between a human and an AI research assistant. "\
                    "The AI gives short and conscise response in academic literature style. ",
                "conversations": []
            },
            prompt = "Summarize the following paper in about 100 words, "\
                "your summary should focus on the motivation and contribution. "\
                "Don't mention title."
                f"Here is the paper: {pdf_txt}",
            model_name = "gpt-3.5-turbo"
            # model_name="vicuna-13b"
        )
        self.logger.debug(f"PDFtext: {pdf_txt}")

        if res is None:
            self.write("ERROR: iRBM server error.")
            return
        
        assert res is not None
        self.logger.info(f"Generating summary for {dp.title} ...")
        summary_txt += "Title: " + dp.title + "\n"
        self.write(summary_txt)
        for msg in res:
            summary_txt += msg      # save to cache
            self.write(msg)
            self.flush()  # Flush the response buffer to send the chunk immediately

        with open(summary_txt_path, "w") as fp:
            self.logger.info(f"Saving summary to {summary_txt_path} ...")
            fp.write(summary_txt)

        self.finish()  # Signal the end of the response
        return