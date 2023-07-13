import pybtex.database
from datetime import date
from typing import TypedDict, Optional
from . import refparser
from .utils import randomAlphaNumeric
from .customError import RBMDocTypeNotSupportedError
import warnings, logging
import nbib
from pybtex.database import BibliographyData, Entry
from pylatexenc import latex2text
import multiprocessing as mp

def checkBibtexValidity(bib_str: str) -> bool:
    """
    Check if the bib string is valid
    """
    try:
        bib_parser = BibParser()
        _ = bib_parser(bib_str)[0]
        return True
    except:
        return False

class BibParser:
    logger = logging.getLogger("rbm")
    def __init__(self, mode = "single"):
        self.mode = mode
    
    @classmethod
    def removeAbstract(cls, bib_str: str) -> str:
        """
        Remove abstract from bib string
        """
        bib_data = pybtex.database.parse_string(bib_str, bib_format="bibtex")
        for k in bib_data.entries.keys():
            if "abstract" in bib_data.entries[k].fields:
                bib_data.entries[k].fields.pop("abstract")
        return bib_data.to_string("bibtex")
    
    def __call__(self, bib_str: str):
        """
            datapoint: {
                "entry": <str>,
                "title": <str>,
                "year": <str>,
                "authors": <list[str]>,  # May contain ", [ ]"
            }
            other possible entries: 
                "journal": tuple(<str>),
                "doi": <str>,
                "booktitle": <str>,
                "pages": <>,
                "abstract": <str>
        """
        bib_data = pybtex.database.parse_string(bib_str, bib_format="bibtex")
        if len(bib_data.entries.keys()) >1 and self.mode == "single":
            warnings.warn("During parsing bib strings, multiple entries found, but single mode is assumed")

        bibs = []
        for k in bib_data.entries.keys():
            _d = bib_data.entries[k]
            if not "year" in _d.fields:
                _d.fields["year"] = date.today().year

            data = {
                "type": _d.type,
                "entry": k,
                "title": _d.fields["title"],
                "year": _d.fields["year"],
                "authors": [str(p) for p in _d.persons["author"]]
            }
            for bib_entry in ["journal", "doi", "booktitle", "pages", "abstract"]:
                if bib_entry in _d.fields:
                    data[bib_entry] = _d.fields[bib_entry],
            bibs.append(data)
        return bibs


class ParsedRef(TypedDict):
    bib: dict
    title: str
    year: str
    authors: list[str]
    publication: Optional[str]
def parseBibtex(bib_single: str) -> ParsedRef:
    """
    parse bibtex and extract useful entries
    """
    parsed = BibParser()(bib_single)[0]
    publication = None
    for k in ["journal", "booktitle"]:
        if k in parsed:
            pub = parsed[k]
            if isinstance(pub, str):
                publication = pub
            elif isinstance(pub, tuple) or isinstance(pub, list):
                publication = pub[0]
            else:
                pass
    return {
        "bib": parsed,
        "title": latex2text.latex2text(parsed["title"]),
        "year": parsed["year"],
        "authors": [ latex2text.latex2text(au) for au in parsed["authors"] ],
        "publication": publication
    }
def parallelParseBibtex(bib_strs: list[str]) -> list[ParsedRef]:
    N_PROC = mp.cpu_count()-1
    with mp.Pool(N_PROC) as p:
        return p.map(parseBibtex, bib_strs)


class BibConverter:
    logger = logging.getLogger("rbm")
    def fromNBib(self, nb: str) -> str:
        parsed = nbib.read(nb.strip("\n") + "\n")
        if not parsed:
            self.logger.error("Error while parsing nbib")
            return ""
        assert len(parsed) == 1, "Only 1 nbib assumed"
        parsed = parsed[0]

        data_dict = {
            "title": parsed["title"],
            "year": parsed["publication_date"][:4],
            "author": " and ".join( a["author"] for a in parsed["authors"] ),
        }
        
        if "Journal Article" in parsed["publication_types"] :
            # for article
            doc_type = "article"
            for k in [["volume", "journal_volume"],
                      ["issue", "journal_issue"],
                      ["number", "journal_issue"]]:
                try:
                    data_dict[k[0]] = parsed[k[1]]
                except:
                    self.logger.error("Could not find {} while parsing nbib".format(k[1]))
        else:
            # To change later
            raise RBMDocTypeNotSupportedError("Not supported document type {}".format(parsed["publication_types"]))

        # try other format
        for k in ["journal", "journal_abbreviated", "abstract", "pages", "doi"]:
            try:
                data_dict[k] = parsed[k]
            except:
                self.logger.error("Could not find key {} while parsing nbib".format(k))

        data = []
        for k, v in data_dict.items():
            data.append((k, v))

        bib_data = BibliographyData({
            f"{data_dict['year']}_{randomAlphaNumeric(5)}":
            Entry(doc_type, data)
        })
        return bib_data.to_string("bibtex")
    
    def fromEndNote(self, en: str):
        parser = refparser.EndnoteParser()
        return parser.toBibtex(en)
