
from .interface import ParserBase, RefDict
import re
import functools


class EndnoteParser(ParserBase):

    pattern = re.compile('^%[0-9|A-Z] ', re.M)

    def checkFormat(self, entry: str) -> bool:
        ## https://github.com/collective/bibliograph.parsing/blob/master/bibliograph/parsing/parsers/endnote.py
        all_tags = re.findall(self.pattern, entry)
        # Should always start w/ '%0' and have at least one author '%A',
        # a year (date) '%D' and a title '%T'
        required = ('%A ', '%D ', '%T ')
        if len(all_tags) and all_tags[0] == '%0 ' and \
                functools.reduce(lambda i, j: i and j, [r in all_tags for r in required]):
            return True
        else:
            return False
    
    def parseEntry(self, entry: str) -> RefDict:
        assert self.checkFormat(entry)
        lines = [line for line in entry.split('\n') if re.findall(self.pattern, line)]

        res = {}

        for line in lines:
            field_code = line[:2]
            content = line[3:]

            if field_code == r"%0":
                res["type"] = content
            elif field_code == r"%D":
                res["year"] = content
            elif field_code == r"%A":
                if "authors" in res:
                    res["authors"].append(content)
                else:
                    res['authors'] = [content]
            elif field_code == r"%T":
                res["title"] = content
            elif field_code == r"%J":
                res["journal"] = content
            elif field_code == r"%V":
                res["volume"] = content
            elif field_code == r"%P":
                res["pages"] = content
            elif field_code == r"%R":
                res["doi"] = content
            elif field_code == r"%B":
                res["secondary_title"] = content
            elif field_code == r"%I":
                res["publisher"] = content
            elif field_code == r"%N":
                res["issue"] = content
            elif field_code == r"%K":
                res["keywords"] = content
            elif field_code == r"%X":
                res["abstract"] = content
            elif field_code == r"%C":
                res["place_published"] = content
            elif field_code == r"%E":
                res["editor"] = content
            elif field_code == r"%F":
                res["label"] = content
        
        assert "authors" in res
        res["author"] = " and ".join(res["authors"])
        
        return res