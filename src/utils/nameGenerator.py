"""
The tools that deals with file names in the database
"""
from typing import List

class fileGeneratorBase:
    def __init__(self, title: str, year: int, authors: List[str]):
        """
        - title: The title of the paper
        - year: the publish year
        - authors: list of authors
        """
        self.title = title
        self.year = year
        self.authors = authors
        return None

    def generateBaseName(self):
        year = str(self.year)
        author = authors[0].replace(" ", "_")
