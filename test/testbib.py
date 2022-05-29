import arxiv
from pybtex.database import BibliographyData, Entry
from datetime import date

# ieee, arxiv

paper_ids = ["2108.06753v1", "2003.13659", "sdfasdf"]
results = arxiv.Search(id_list=paper_ids).results()
for id, result in zip(paper_ids, results):
    print(result)

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

    print(bib_data.to_string('bibtex'))
    
    print(result.pdf_url)

    # result.download_pdf()
