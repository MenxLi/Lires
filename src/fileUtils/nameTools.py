"""
The tools that deals with file names in the database
"""
from typing import List, Union
from ..paths import DATA_PATH

class fileGeneratorBase:
    def __init__(self, title: str, year: Union[int, str], authors: List[str]):
        """
        - title: The title of the paper
        - year: the publish year
        - authors: list of authors
        """
        self.title = title
        self.year = year
        self.authors = authors
        self.base_name = self.generateBaseName()
        return None

    def generateBaseName(self):
        year = str(self.year)
        author = self.authors[0].replace(" ", "_").replace(",", "^")
        title = self.title.replace(" ", "_")
        base_name = "{}-{}-{}".format(year, author, title)
        return base_name

class fileGenerator(fileGeneratorBase):
    FOLDERNAME = "files"
    def __init__(self, title: str, year: Union[int, str], authors: List[str]):
        super().__init__(title, year, authors)
        # file names
        file_fn_nosuffix = "file@"+self.base_name
        comment_fn = "comment@"+self.base_name+".md"
        bib_fn = "bib@"+self.base_name+".bib"
        info_fn = "info@"+self.base_name+".json"

    def generateDefaultFiles(self):
        pass