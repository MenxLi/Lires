# API
使用Javascript API实现脚本化操作。

在软件的关于页面中可以下载API文件包，解压后包含程序示例`main.mjs`和相关API库文件。
所有接口均包含TS类型定义，方法名和参数名均有语义化命名，方便使用。

::: info
前端页面即使用此API进行数据交互，你甚至可以基于此接口开发自己的前端页面😊
:::

::: warning
API文件包下载过程中即在`main.mjs`中包含了用户授权信息，因此请勿直接将API文件包分享给他人。
:::


## 示例
抓取ArXiv上最新50条CV论文信息，并加入到数据库中。

::: details 前置代码
安装依赖
```sh
npm install fast-xml-parser
```
工具函数
```javascript
import { XMLParser } from 'fast-xml-parser';
export async function fetchArxivFeed(
    maxResults = 10,
    searchQuery = 'cat:cs.AI OR cat:cs.CV',
    sortBy = 'submittedDate',
    sortOrder = 'descending',
  ){
    const query = `search_query=${encodeURIComponent(searchQuery)}&sortBy=${sortBy}&sortOrder=${sortOrder}&max_results=${maxResults}`;
    const apiUrl = `https://export.arxiv.org/api/query?${query}`;
    const response = await fetch(apiUrl, { method: 'GET', });
    const xmlData = await response.text();
    const parser = new XMLParser();
    const parsedData = parser.parse(xmlData);
    let entries = parsedData.feed.entry;
    if (!Array.isArray(entries)) { entries = [entries]; }
    function getAuthors(entry){
      if (Array.isArray(entry.author)) { return entry.author.map((author) => author.name); }
      else if (entry.author) { return [entry.author.name]; }
      else return [];
    }
    if (entries && Array.isArray(entries)) {
      const articles = entries.map((entry) => {
        const id = entry.id.split('/').pop().split('v')[0];
        const link = entry.id;
        const title = entry.title;
        const abstract = entry.summary;
        const authors = getAuthors(entry);
        const updatedTime = entry.updated;
        const publishedTime = entry.published;
        const bibtex = `@article{${id},
        title = {${title}},
        author = {${authors.join(' and ')}},
        journal = {arXiv preprint arXiv:${id}},
        year = {${publishedTime.slice(0, 4)}},
        url = {${link}}
        }`;
        return { id, link, title, abstract, authors, updatedTime, publishedTime, bibtex};
      });
  
      return articles;
    } else { throw new Error('Invalid feed data'); }
}
```
:::

```javascript
// Lires-API v1.7.3 (Accessed: ...)
import { ServerConn } from "./lib/api.js";

const context = {
    endpoint: "https://...",
    key: "..."
}
// lires 服务器连接对象
const conn = new ServerConn(()=>context.endpoint, ()=>context.key)

// 抓取最新50条ArXiv上的文章
const articles = await fetchArxivFeed(50, 'cat:cs.CV');

for (const article of articles) {
    try{
        // 添加到数据库
        await conn.updateDatapoint(null, {
          bibtex: article.bibtex, 
          tags: ['arxiv-collect'], 
          url: article.link
        });
        console.log(`Article "${article.id}" added to the database.`);
    }
    catch(e){
        // 如果返回409则说明已存在
        console.error(`Error adding article "${article.id}" to the database: ${e}`);
    }
}
```