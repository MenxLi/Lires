
from abc import ABC, abstractmethod
from typing import Dict, Type, List, Optional
import arxiv
import os, argparse, logging, sys
from datetime import date
from pybtex.database import BibliographyData, Entry

import requests, urllib
from bs4 import BeautifulSoup

from lires.core.bibReader import BibParser
from lires.core.fileTools import addDocument, DBConnection
from lires.core.fileToolsV import FileManipulatorVirtual
from lires.core.dataClass import DataPoint, DataBase
from lires.confReader import TMP_DIR, getConfV, getServerURL
from lires.core.utils import sssUUID
from lires.core import globalVar as G

class DocCollector(ABC):
    DOC_EXT = ".pdf"
    retrive_key: str
    logger = G.logger_rbm
    def __init__(self, retrive_key: str):
        self.retrive_key = retrive_key

    @abstractmethod
    def retrive(self) -> bool:
        """
        Does the connection and retrive the data
        prepare as much as possible for other things such as bibtex, pdf dowload etc.
        """
        ...

    @abstractmethod
    def bibtexStr(self) -> str:
        """
        Get bibtex string
        """
        ...

    @abstractmethod
    def downloadDoc(self, dst: str) -> bool:
        """
        download file (may be pdf)
         - dst: destination file path
        """
        ...

    @abstractmethod
    def url(self) -> str:
        ...

class ArXivCollector(DocCollector):
    def retrive(self) -> bool:
        paper_ids = [self.retrive_key]
        results = arxiv.Search(id_list = paper_ids).results()
        try:
            for id, result in zip(paper_ids, results):
                key = '{}{}{}'.format(result.authors[0].name.split(' ')[-1].lower(),result.published.year,result.title.split(' ')[0].lower())
                if key.endswith(','):
                    key = key[:-1]

                abstract = result.summary.replace('\n',' ').replace('{',' ').replace('}', ' ')

                bib_data = BibliographyData({
                    key: Entry('article', [
                        ('author', ' and '.join([a.name for a in result.authors])),
                        ('title', ' '.join(result.title.replace('\n',' ').split())),
                        ('year', '{:04d}'.format(result.published.year)),
                        ('eprint', id),
                        ('archivePrefix', 'arXiv'),
                        ('primaryClass', result.primary_category),
                        ('abstract', abstract),
                        ('publisher', "arXiv"),
                        ('date', '{:04d}-{:02d}-{:02d}'.format(date.today().year,date.today().month,date.today().day))
                    ])
                })
                self.__result = result
                self.__bib_str = bib_data.to_string('bibtex')
            return True
        except arxiv.arxiv.HTTPError:
            return False
        
    def bibtexStr(self) -> str:
        return self.__bib_str

    def downloadDoc(self, dst: str) -> bool:
        dir_path = os.path.dirname(dst)
        file_name = os.path.basename(dst)
        self.__result.download_pdf(dir_path, file_name)
        return True

    def url(self) -> str:
        return self.__result.pdf_url

class WebCollector(DocCollector):
    """
    Collect data from web
    retrive_key: url
    """
    def retrive(self) -> bool:
        url = self.retrive_key
        r = requests.get(url)
        if r.status_code != 200:
            self.logger.error(f"WebCollector: got status code {r.status_code}")
            return False
        soup = BeautifulSoup(r.text, 'html.parser')

        # GET TITLE
        title = None
        if soup.findAll("title"):
            title = soup.find("title").string
        if not title:
            if soup.findAll("h1"):
                title = soup.find("h1").string
        if not title:
            if soup.findAll("h2"):
                title = soup.find("h2").string
        if not title:
            title = "unknown" + "-" + url[:20]
        
        # GET AUTHOR
        author = None
        if soup.findAll("meta", {"name": "author"}):
            author = soup.find("meta", {"name": "author"})['content']
        if not author:
            # traverse all content and find the first author
            for content in soup.findAll("meta", {"name": "content"}):
                if content['content'].lower().startswith("author"):
                    author = content['content'][7:]
                    break
        if not author:
            # traverse body and find the first author / 作者
            for content in soup.findAll("body"):
                for content2 in content.findAll("p"):
                    if content2.string.lower().startswith("author"):
                        author = content2.string[7:]
                        break
                    if content2.string.lower().startswith("作者"):
                        author = content2.string[3:]
                        break
                if author:
                    break
        if not author:
            author = "unknown"

        self.bib_data = BibliographyData({
            sssUUID(): Entry('misc', [
                ('title', title),
                ('howpublished', 'Available at \\url{{{}}}'.format(url)),
                ('year', '{:04d}'.format(date.today().year)),
                ('author', author),
                ('date', '{:04d}-{:02d}-{:02d}'.format(date.today().year,date.today().month,date.today().day))
            ])})
        return True
        
    def bibtexStr(self) -> str:
        return self.bib_data.to_string('bibtex')
    
    def downloadDoc(self, dst: str) -> bool:
        self.logger.warn("WebCollector: downloadDoc not implemented")
        return False
    
    def url(self) -> str:
        return self.retrive_key

class LiresRetriver:
    KEY_COLLECTOR: Dict[str, Type[DocCollector]]
    KEY_COLLECTOR = {
        "arxiv": ArXivCollector,
        "web": WebCollector,
    }
    logger = G.logger_rbm
    def __init__(self, retrive_str: str):
        collector_key = retrive_str.split(":")[0].lower()
        retrive_key = retrive_str[len(collector_key) + 1:]

        self.collector = self.KEY_COLLECTOR[collector_key.lower()](retrive_key)

    def run(
            self, 
            database: Optional[DataBase] = None,
            download_doc: bool = False, 
            tags: List[str] = [], 
            uid: Optional[str] = None, 
            check_duplicate: bool = True
            ) -> str:
        """
        Return data uuid or ''
        """
        if database is None:
            __new_database = True   # indicate if the database is newly created
            database_dir = getConfV("database")
            database = DataBase(database_dir, force_offline = True)
        else:
            __new_database = False

        self.logger.debug("Retrieving data")
        collector = self.collector
        if not collector.retrive():
            # Failed
            return ''
        
        # Generate data
        bib_str = collector.bibtexStr()
        _doc_info = {}
        if uid is not None:
            _doc_info["uuid"] = uid
        uid = addDocument(
            database.conn, 
            bib_str, 
            doc_info = _doc_info, 
            check_duplicate = check_duplicate
            )
        if uid is None:
            self.logger.error("Failed to add document to database, maybe duplicated?")
            if __new_database:
                # clean up
                database.destroy()
            return ''

        dp = database.add(uid)
        dp.fm.setWebUrl(collector.url())
        dp.fm.writeTags(tags)
        dp.loadInfo()   # reload info because tags are changed
        self.logger.debug("File generated: {}".format(dp.uuid))

        ret = dp.uuid
        # Add file if needed
        if download_doc:
            f_path_tmp = os.path.join(TMP_DIR, sssUUID() + collector.DOC_EXT)
            self.logger.debug("Starting download...")
            try:
                if collector.downloadDoc(f_path_tmp):
                    if dp.addFile(f_path_tmp):
                        if os.path.exists(f_path_tmp):
                            self.logger.debug("Removing tmp file: {}".format(f_path_tmp))
                            os.remove(f_path_tmp)
                    else:
                        ret = ''
            except Exception as e:
                self.logger.error("Failed to download file: {}".format(e))
        
        if __new_database:
            # clean up
            database.destroy()
        return ret

def exec(
        retrive_str: str, 
        download_doc: bool = False,
        tags: List[str] = [],
        uid: Optional[str] = None
        ) -> str:
    retriver = LiresRetriver(retrive_str)
    return retriver.run(
        download_doc = download_doc,
        tags = tags,
        uid = uid,
    )

def main():
    _description = "automatically add entry to the database by id"
    parser = argparse.ArgumentParser("rbm-collect", description = _description)
    parser.add_argument("retrive", help = "retrive instruction, e.g. arxiv:[....]")
    parser.add_argument("-s", "--server_run", action = "store_true", default = False, help = "Run on the server side")
    parser.add_argument("-d", "--download", action = "store_true", default = False, help = "download file (please consider network condition)")
    parser.add_argument("-t", "--tags", nargs = "+", type = str, default = [], help = "tags for downloaded data")
    parser.add_argument("-L", "--log_level", action= "store", type = str, default="INFO", help = "log level")
    # t = "arxiv:2108.06753v1"
    args = parser.parse_args()

    logger = logging.getLogger("rbm")
    handler = logging.StreamHandler(sys.stdout)
    logger.setLevel(getattr(logging, args.log_level))
    handler.setLevel(getattr(logging, args.log_level))
    fomatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(fomatter)
    logger.addHandler(handler)

    if args.server_run:
        import requests, json
        from lires.core.encryptClient import generateHexHash
        post_args = {
            "key": generateHexHash(getConfV("access_key")),
            "retrive": args.retrive,
            "tags": json.dumps(args.tags),
            "download_doc": "true" if args.download else "false",
            # "uuid": args.retrive,
        }
        addr = getServerURL()
        post_addr = "{}/collect".format(addr) 
        res = requests.post(post_addr, params = post_args)
        if not res.ok:
            logger.error(f"Failed requesting {post_addr} ({res.status_code}).")
        else:
            logger.info("Success")
    else:
        if exec(args.retrive, download_doc=args.download, tags=args.tags):
            logger.info("Success")
        else:
            logger.error("Failed")

if __name__ == '__main__':
    main()
    





