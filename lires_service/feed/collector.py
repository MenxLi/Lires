
from dataclasses import dataclass
import aiohttp, urllib.parse
import xml.etree.ElementTree as ET
import string


@dataclass
class ArticleInfo:
    id: str
    bibtex: str
    link: str
    tags: list[str]

async def fetchArxiv(
    max_results=10, 
    search_query='cat:cs.AI OR cat:cs.CV', 
    sort_by='submittedDate', 
    sort_order='descending'
    ) -> list[ArticleInfo]:
    query = f'search_query={urllib.parse.quote(search_query)}&sortBy={sort_by}&sortOrder={sort_order}&max_results={max_results}'
    api_url = f'https://export.arxiv.org/api/query?{query}'

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url, verify_ssl=False) as response:
            xml_data = await response.text()

    root = ET.fromstring(xml_data)
    entries = root.findall('{http://www.w3.org/2005/Atom}entry')

    def get_authors(entry) -> list[str]:
        authors = entry.findall('{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name')
        return [author.text for author in authors]
    
    def arxiv2Bibtex(
        id: str,
        title: str,
        authors: list[str],
        abstract: str,
        link: str,
        published_time: str,
    ) -> str:
        article_template = string.Template(
"""
@article{$id,
    title = "$title",
    author = "$authors",
    abstract = "$abstract",
    journal = "arXiv preprint arXiv:$id",
    year = "$year",
    url = "$link"
}
"""
        )

        def formatIllegalChar(s: str) -> str:
            # check if brackets are balanced
            if s.count('{') != s.count('}'):
                s = s.replace('{', '').replace('}', '')
                print(f'Warning: unbalanced brackets in {s}')

            return s.replace('"', "'")

        ret = article_template.safe_substitute(
            id=id,
            title=formatIllegalChar(title),
            authors=' and '.join([
                formatIllegalChar(author)
                for author in
                authors]),
            abstract=formatIllegalChar(abstract),
            year=published_time.split('-')[0],
            link=link,
        )
        return ret

    articles = []
    for entry in entries:
        id = entry.find('{http://www.w3.org/2005/Atom}id')
        assert id is not None; assert id.text is not None; id = id.text.split('/').pop().split('v')[0]
        link = entry.find('{http://www.w3.org/2005/Atom}id')
        assert link is not None; assert link.text; link = link.text
        title = entry.find('{http://www.w3.org/2005/Atom}title')
        assert title is not None; assert title.text; title = title.text
        abstract = entry.find('{http://www.w3.org/2005/Atom}summary')
        assert abstract is not None; assert abstract.text; abstract = abstract.text
        authors = get_authors(entry)
        published_time = entry.find('{http://www.w3.org/2005/Atom}published')
        assert published_time is not None; assert published_time.text; published_time = published_time.text
        # updated_time = entry.find('{http://www.w3.org/2005/Atom}updated').text

        tags = entry.findall('{http://www.w3.org/2005/Atom}category')
        tags = [tag.attrib['term'] for tag in tags]
        

        articles.append(
            ArticleInfo(
                id=id,
                bibtex=arxiv2Bibtex(id, title, authors, abstract, link, published_time),
                link=link,
                # tags=[f'arxiv-{t.strip()}' for t in search_query.split('OR')],
                tags = [f'arxiv->{tag}' for tag in tags],
            )
        )

    return articles

if __name__ == '__main__':
    import asyncio
    articles = asyncio.run(fetchArxiv())
    print(articles)