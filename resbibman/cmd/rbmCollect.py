
from abc import ABC, abstractmethod
from typing import Dict, Type, List
import arxiv
import os, argparse, logging, sys
from datetime import date
from pybtex.database import BibliographyData, Entry

from resbibman.core.bibReader import BibParser
from resbibman.core.fileTools import FileGenerator
from resbibman.core.fileToolsV import FileManipulatorVirtual
from resbibman.core.dataClass import DataPoint
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
        Performance the connection and retrive the data
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
        collector_key, retrive_key = retrive_str.split(":")
        self.collector = self.KEY_COLLECTOR[collector_key.lower()](retrive_key)

    def run(self, download_doc: bool = False, tags: List[str] = []) -> str:
        """
        Return data path or ''
        """
        database_dir = getConfV("database")
        collector = self.collector
        self.logger.debug("Retrieving data")
        if not collector.retrive():
            # Failed
            return ''
        # Generate data
        bib_str = collector.bibtexStr()
        bib = BibParser()(bib_str)[0]
        fg = FileGenerator(None, bib["title"], bib["year"], bib["authors"])
        fg.generateDefaultFiles(database_dir)
        # Add bibtex and write information
        fm = FileManipulatorVirtual(fg.dst_path)
        fm._forceOffline()
        fm.screen()
        fm.writeBib(collector.bibtexStr())
        fm.setWebUrl(collector.url())
        fm.writeTags(tags)
        self.logger.debug("File generated: {}".format(fm.path))
        # Add file if needed
        if download_doc:
            dp = DataPoint(fm)
            dp._forceOffline()
            f_path_tmp = os.path.join(TMP_DIR, sssUUID() + collector.DOC_EXT)
            self.logger.debug("Starting download...")
            if collector.downloadDoc(f_path_tmp):
                # will delete f_path_tmp
                print(f_path_tmp)
                if dp.addFile(f_path_tmp):
                    return fm.path
                else:
                    return ''
        return fm.path

def exec(retrive_str: str, **kwargs) -> str:
    retriver = RBMRetriver(retrive_str)
    return retriver.run(**kwargs)

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

    _args = {
        "tags": args.tags,
        "download_doc": args.download
    }
    if args.server_run:
        import requests, json
        from resbibman.core.encryptClient import generateHexHash
        post_args = {
            "key": generateHexHash(getConfV("access_key")),
            "cmd": "rbm-collect",
            "uuid": "_",
            "args": json.dumps([args.retrive]),
            "kwargs": json.dumps(_args)
        }
        addr = "http://{}:{}".format(getConfV("host"), getConfV("port"))
        post_addr = "{}/cmdA".format(addr) 
        res = requests.post(post_addr, params = post_args)
        if not res.ok:
            logger.warning(f"Failed requesting {post_addr} ({res.status_code}).")
        else:
            logger.info("Success")
    else:
        if exec(args.retrive, **_args):
            logger.info("Success")
        else:
            logger.warning("Failed")

if __name__ == '__main__':
    main()
    





