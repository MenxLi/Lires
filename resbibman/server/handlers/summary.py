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

    def get(self):
        if not self.checkKey():
            raise tornado.web.HTTPError(403)
        return self.write(self.summary_html_template)

class SummaryPostHandler(tornado.web.RequestHandler, RequestHandlerBase):
    def post(self):
        if not self.checkKey():
            self.write("ERROR: Invalid key.")
            raise tornado.web.HTTPError(403)
        # Set the appropriate headers to enable streaming
        self.set_header('Content-Type', 'text/plain')
        self.set_header('Cache-Control', 'no-cache')

        uuid = self.get_argument("uuid")
        force = self.get_argument("force", "false").lower() == "true"
        model_name = self.get_argument("model", "gpt-3.5-turbo")

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

        def generateSimilar(summary_txt, except_uuid=""):
            # find similar papers
            self.write("\n<hr>")
            similar = iconn.queryFeatureIndex(summary_txt, n_return=9)
            if similar is None:
                self.write("ERROR: iRBM server error while finding similar papers.")
                return
            self.write("<h3>Similar papers:</h3>")
            self.flush()

            uids, scores = similar["uids"], similar["scores"]
            for uuid, score in zip(uids, scores):
                if uuid == except_uuid:
                    continue
                dp = self.db[uuid]
                self.write(f"<a href='{dp.getDocShareLink(with_base=False)}'>{dp.title}</a> ({score:.2f})<br>")
                self.flush()
        
        # a cache for summary
        summary_txt_path = os.path.join(DOC_SUMMARY_DIR, uuid + ".txt")
        if os.path.exists(summary_txt_path) and not force:
            with open(summary_txt_path, "r") as fp:
                summary_txt = fp.read()
            for line in summary_txt.split("\n"):
                self.write(line)
                self.flush()
            generateSimilar(summary_txt, except_uuid=uuid)
            self.finish()
            return
        
        assert dp.file_path
        if model_name == "gpt-3.5-turbo":
            __max_words = 2048
        elif model_name == "gpt-4":
            __max_words = 4096
        else:
            __max_words = 768
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
            model_name = model_name
        )
        self.logger.debug(f"PDFtext: {pdf_txt}")

        if res is None:
            self.write("ERROR: iRBM server error.")
            return
        
        assert res is not None
        self.logger.info(f"Generating summary for {dp.title} ...")
        # summary_txt += f"<h3>Title: {dp.title}</h3>"
        self.write(summary_txt)
        for msg in res:
            summary_txt += msg      # save to cache
            self.write(msg)
            self.flush()  # Flush the response buffer to send the chunk immediately

        with open(summary_txt_path, "w") as fp:
            self.logger.info(f"Saving summary to {summary_txt_path} ...")
            fp.write(summary_txt)
        
        generateSimilar(summary_txt, except_uuid=uuid)

        self.finish()  # Signal the end of the response
        return
