from ._base import *
from tornado import template
from dataclasses import dataclass
import os
from lires.config import getConf
from ..path_config import ASSETS_DIR

@dataclass
class ShareEntry:
    uid: str
    title: str
    year: int | str
    authors: list[str]
    publication: str
    abstract: str
    links: dict[str, str]

class ShareHandler(RequestHandlerBase):
    with open(os.path.join(ASSETS_DIR, 'share.template.html')) as f:
        share_page_template = template.Template(f.read())

    @authenticate(enabled = not getConf()['allow_public_query'])
    async def get(self):

        # get user
        user_id = await self.inferUserId()
        user = await self.user_pool.getUserById(user_id)
        if user is None:
            await self.logger.error(f"User not found on share request: {user_id}")
            return self.write_error(404)
        
        # get share entries
        entry_ids = self.get_argument("uids", "").split(",")
        db = await self.db()
        share_entries = []
        for uid in entry_ids:
            try:
                dp = await db.get(uid)
                links = {}
                if dp.has_file:
                    links['fulltext'] = f"/doc/{uid}?u={user_id}"
                if dp.summary.url:
                    links['link'] = dp.summary.url
                links.update({
                    'bibtex': f"/bibtex/{uid}?u={user_id}",
                    'scholar': f"https://scholar.google.com/scholar?q={dp.title}"
                })
                share_entries.append(ShareEntry(
                    uid = uid,
                    title = dp.title,
                    year = dp.year,
                    authors = dp.authors,
                    publication = dp.publication if dp.publication else "", 
                    abstract=await dp.fm.readAbstract(),
                    links = links
                ))
            except self.Error.LiresEntryNotFoundError:
                await self.logger.warning(f"Share entry not found: {uid}")

        self.write(self.share_page_template.generate(
            user_name = (await user.info())['name'],
            share_entries = share_entries,
        ))

class BibtexHandler(RequestHandlerBase):
    @authenticate(enabled = not getConf()['allow_public_query'])
    async def get(self, uid): 
        db = await self.db()
        dp = await db.get(uid)
        self.set_header("Content-Type", "text/plain")
        self.write(dp.summary.bibtex)