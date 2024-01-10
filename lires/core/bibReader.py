import pybtex.database
from datetime import date
from typing import TypedDict, Optional, Callable
from . import refparser
from .base import LiresBase
import warnings, logging
import nbib
from pybtex.database import BibliographyData, Entry
import pybtex.scanner
from pylatexenc import latex2text
import multiprocessing as mp
from ..utils import randomAlphaNumeric

def checkBibtexValidity(bib_str: str, onerror: Optional[Callable[[str], None]] = None) -> bool:
    """
    Check if the bib string is valid
    """
    if onerror is None:
        onerror = lambda x: None
    try:
        bib_parser = BibParser()
        _ = bib_parser(bib_str)[0]
        return True
    except IndexError as e:
        onerror(f"IndexError while parsing bibtex, check if your bibtex info is empty: {e}")
        return False
    except pybtex.scanner.PrematureEOF:
        onerror(f"PrematureEOF while parsing bibtex, invalid bibtex")
        return False
    except KeyError:
        onerror(f"KeyError. (Year and title must be provided)")
        return False
    except Exception as e:
        onerror("Error when parsing bib string: {}".format(e))
        return False

class BibParser(LiresBase):
    logger = LiresBase.loggers().core
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
                self.logger.warning("No year found in bib entry {}".format(k))
                _d.fields["year"] = date.today().year
            
            if not "author" in _d.persons:
                self.logger.warning("No author found in bib entry {}".format(k))
                _d.persons["author"] = ["_"]

            data = {
                "type": _d.type,
                "entry": k,
                "title": _d.fields["title"],
                "year": _d.fields["year"],
                "authors": [str(p) for p in _d.persons["author"]]
            }
            for bib_entry in ["journal", "doi", "booktitle", "pages", "abstract", "eprint"]:
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
    for k in ["journal", "booktitle", "eprint"]:
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
    if N_PROC > 8:
        N_PROC = 8
    with mp.Pool(N_PROC) as p:
        return p.map(parseBibtex, bib_strs)


class BibConverter(LiresBase):
    logger = LiresBase.loggers().core
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
            raise self.Error.LiresDocTypeNotSupportedError("Not supported document type {}".format(parsed["publication_types"]))

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
