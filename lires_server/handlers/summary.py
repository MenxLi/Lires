from ._base import *
import os
from lires.core.pdfTools import getPDFText
from lires.config import DOC_SUMMARY_DIR

class SummaryHandler(RequestHandlerBase):

    @keyRequired
    async def post(self):

        # Set the appropriate headers to enable streaming
        self.set_header('Content-Type', 'text/plain')
        self.set_header('Cache-Control', 'no-cache')

        uuid = self.get_argument("uuid")
        force = self.get_argument("force", "false").lower() == "true"
        model_name = self.get_argument("model", "DEFAULT")

        if not await self.db.has(uuid):
            self.write("ERROR: No such paper.")
            return

        dp = await self.db.get(uuid)

        user_info = await self.userInfo()
        if not user_info["is_admin"]:
            is_allowed = await self.checkTagPermission(dp.tags, user_info["mandatory_tags"], raise_error=False)
            if not is_allowed:
                self.write("ERROR: Permission denied.")
                return

        istatus = await self.iconn.status
        if not (istatus and istatus['status']):
            self.write("ERROR: LiresAI server not running.")
            return
        
        if not (await dp.fm.filePath() and dp.summary.file_type == ".pdf"):
            self.write("ERROR: No pdf file.")
            return

        # a cache for summary
        summary_txt_path = os.path.join(DOC_SUMMARY_DIR, uuid + ".txt")
        if os.path.exists(summary_txt_path) and not force:
            with open(summary_txt_path, "r", encoding='utf-8') as fp:
                summary_txt = fp.read()
            for line in summary_txt.split("\n"):
                self.write(line)
                self.flush()
            # generateSimilar(summary_txt, except_uuid=uuid)
            self.finish()
            return
        
        assert await dp.fm.filePath()
        if "16k" in model_name:
            __max_words = 16384
        elif "32k" in model_name:
            __max_words = 32768
        elif model_name == "gpt-3.5-turbo":
            __max_words = 2048
        elif model_name == "gpt-4":
            __max_words = 4096
        else:
            __max_words = 1024
        pdf_txt = await getPDFText(await dp.fm.filePath(), __max_words)   # type: ignore
        if len(pdf_txt) < 100:
            self.write("ERROR: Not enough content in the paper.")
            return

        summary_txt = ""
        res = self.iconn.chat(
            conv_dict={
                "system": "A conversation between a human and an AI research assistant. "\
                    "The AI gives short and conscise response in academic literature style. ",
                "conversations": []
            },
            prompt = "Summarize the following paper in about 100 words, "\
                "your summary should focus on the motivation and contribution. "\
                "Don't mention title."
                f"Here is the paper: {pdf_txt}",
            model_name = model_name # type: ignore
        )
        await self.logger.debug(f"PDFtext: {pdf_txt}")

        if res is None:
            self.write("ERROR: LiresAI server error.")
            return
        
        assert res is not None
        await self.logger.info(f"Generating summary for {dp.title} ...")
        # summary_txt += f"<h3>Title: {dp.title}</h3>"
        self.write(summary_txt)

        async for msg in res:
            summary_txt += msg      # save to cache
            self.write(msg)
            self.flush()  # Flush the response buffer to send the chunk immediately

        with open(summary_txt_path, "w", encoding='utf-8') as fp:
            await self.logger.info(f"Saving summary to {summary_txt_path} ...")
            fp.write(summary_txt)
        
        self.finish()  # Signal the end of the response
        return
