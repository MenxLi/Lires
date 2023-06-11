
from abc import ABC, abstractmethod
from typing import Dict, Type, List, Optional
import arxiv
import os, argparse, logging, sys
from datetime import date
from pybtex.database import BibliographyData, Entry

from resbibman.core.bibReader import BibParser
from resbibman.core.fileTools import addDocument, DBConnection
from resbibman.core.fileToolsV import FileManipulatorVirtual
from resbibman.core.dataClass import DataPoint, DataBase
from resbibman.confReader import TMP_DIR, getConfV
from resbibman.core.utils import sssUUID
from resbibman.core import globalVar as G

class DocCollector(ABC):
    DOC_EXT = ".pdf"
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

class RBMRetriver:
    KEY_COLLECTOR: Dict[str, Type[DocCollector]]
    KEY_COLLECTOR = {
        "arxiv": ArXivCollector
    }
    logger = G.logger_rbm
    def __init__(self, retrive_str: str):
        retrive_str = retrive_str.strip().lower()
        collector_key, retrive_key = retrive_str.split(":")
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
        if not database:
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
    retriver = RBMRetriver(retrive_str)
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
        from resbibman.core.encryptClient import generateHexHash
        post_args = {
            "key": generateHexHash(getConfV("access_key")),
            "retrive": args.retrive,
            "tags": json.dumps(args.tags),
            "download_doc": "true" if args.download else "false",
            "uuid": args.retrive,
        }
        addr = "http://{}:{}".format(getConfV("host"), getConfV("port"))
        post_addr = "{}/collect".format(addr) 
        res = requests.post(post_addr, params = post_args)
        if not res.ok:
            logger.error(f"Failed requesting {post_addr} ({res.status_code}).")
        else:
            logger.info("Success")
    else:
        if exec(args.retrive, download_doc=args.download, tags=args.tags, uid=args.retrive):
            logger.info("Success")
        else:
            logger.error("Failed")

if __name__ == '__main__':
    main()
    





