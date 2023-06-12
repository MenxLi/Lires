// Mostly written by chatgpt!
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
export interface ArxivArticleWithFeatures extends ArxivArticle{
  features: number[] | undefined,
}

export async function fetchArxivFeed(
  maxResults: number = 10,
  searchQuery: string = 'cat:cs.CV',
  sortBy: string = 'submittedDate',
  sortOrder: string = 'descending',
): Promise<ArxivArticle[]> {
  // const apiUrl = 'https://export.arxiv.org/api/query?search_query=cat:cs.CV&sortBy=submittedDate&sortOrder=descending&max_results=10';
  const query = `search_query=${encodeURIComponent(searchQuery)}&sortBy=${sortBy}&sortOrder=${sortOrder}&max_results=${maxResults}`;
  const apiUrl = `https://export.arxiv.org/api/query?${query}`;
  const response = await fetch(apiUrl);
  const xmlData = await response.text();

  const parser = new XMLParser();
  const parsedData = parser.parse(xmlData);

  const entries = parsedData.feed.entry;
  if (entries && Array.isArray(entries)) {
    const articles: ArxivArticle[] = entries.map((entry: any) => {
      const id = entry.id.split('/').pop();
      const link = entry.id;
      const title = entry.title;
      const abstract = entry.summary;
      const authors = entry.author.map((author: any) => author.name);
      const updatedTime = entry.updated;
      const publishedTime = entry.published;
      return { id, link, title, abstract, authors, updatedTime, publishedTime };
    });

    return articles;
  } else {
    throw new Error('Invalid feed data');
  }
}