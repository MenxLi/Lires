import pybtex.database
import warnings

class BibParser:
    def __init__(self, mode = "single"):
        self.mode = mode
    
    def __call__(self, bib_str: str):
        """
            datapoint: {
                "entry": <str>,
                "title": <str>,
                "year": <str>,
                "authors": <list|str>,  # May contain ", [ ]"
            }
            other possible entries: 
                "journal": <str>,
                "doi": <str>
        """
        bib_data = pybtex.database.parse_string(bib_str, bib_format="bibtex")
        if len(bib_data.entries.keys()) >1 and self.mode == "single":
            warnings.warn("During parsing bib strings, multiple entries found, but single mode is assumed")

        bibs = []
        for k in bib_data.entries.keys():
            _d = bib_data.entries[k]
            datapoint = {
                "entry": k,
                "title": _d.fields["title"],
                "year": _d.fields["year"],
                "authors": [str(p) for p in _d.persons["author"]]
            }
            for bib_entry in ["journal", "doi"]:
                if bib_entry in _d.fields:
                    datapoint[bib_entry] = _d.fields[bib_entry],
            bibs.append(datapoint)
        return bibs

class BibObj:
    """
    Object representation of the bibliography file
    """
    def __init__(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])


test_str = "@article{li2020automated, \
  title={Automated integration of facial and intra-oral images of anterior teeth}, \
  author={Li, Mengxun and Xu, Xiangyang and Punithakumar, Kumaradevan and Le, Lawrence H and Kaipatur, Neelambar and Shi, Bin}, \
  journal={Computers in Biology and Medicine}, \
  volume={122}, \
  pages={103794}, \
  year={2020}, \
  publisher={Elsevier} \
}"