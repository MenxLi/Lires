import { XMLParser } from 'fast-xml-parser';

export interface ArxivArticle {
  id: string;
  link: string;
  title: string;
  abstract: string;
  authors: string[];
  updatedTime: string;
  publishedTime: string;
}

export async function fetchArxivFeed(
  maxResults: number = 10,
  searchQuery: string = 'cat:cs.AI OR cat:cs.CV',
  sortBy: string = 'submittedDate',
  sortOrder: string = 'descending',
): Promise<ArxivArticle[]> {
  // const apiUrl = 'https://export.arxiv.org/api/query?search_query=cat:cs.CV&sortBy=submittedDate&sortOrder=descending&max_results=10';
  const query = `search_query=${encodeURIComponent(searchQuery)}&sortBy=${sortBy}&sortOrder=${sortOrder}&max_results=${maxResults}`;
  const apiUrl = `https://export.arxiv.org/api/query?${query}`;
  const response = await fetch(apiUrl, { method: 'GET', });
  const xmlData = await response.text();

  const parser = new XMLParser();
  const parsedData = parser.parse(xmlData);

  const entries = parsedData.feed.entry;
  console.log(parsedData)

  // some entries have multiple authors, some have one, (some have none??)
  function getAuthors(entry: any): string[] {
    if (Array.isArray(entry.author)) {
      return entry.author.map((author: any) => author.name);
    }
    else if (entry.author) {
      return [entry.author.name];
    }
    else return [];
  }

  if (entries && Array.isArray(entries)) {
    const articles: ArxivArticle[] = entries.map((entry: any) => {
      const id = entry.id.split('/').pop();
      const link = entry.id;
      const title = entry.title;
      const abstract = entry.summary;
      const authors = getAuthors(entry);
      const updatedTime = entry.updated;
      const publishedTime = entry.published;
      return { id, link, title, abstract, authors, updatedTime, publishedTime};
    });

    return articles;
  } else {
    throw new Error('Invalid feed data');
  }
}