import { fetchArxivPaperByID, bibtexFromArxiv } from "../../core/arxivUtils";

export type BibtexTypes = 'article' | 'inproceedings'
export const getBibtexTemplate = (type: BibtexTypes) => {
        // generate a random bibtex entry
    const entry = Math.random().toString(36).substring(7);
    if (type == "article"){
        return `@article{${entry},
        author = {},
        title = {},
        journal = {},
        year = {${new Date().getFullYear()}},
        volume = {},
        number = {},
        pages = {},
        month = {},
        doi = {},
        }`.replace(/  /g, "");
    }
    else if (type == "inproceedings"){
        return `@inproceedings{${entry},
        author = {},
        title = {},
        booktitle = {},
        year = {${new Date().getFullYear()}},
        editor = {},
        volume = {},
        number = {},
        series = {},
        pages = {},
        }`.replace(/  /g, "");
    }
    else {
        return "";
    }
}


interface CollectRes{
    bibtex: string,
    url: string
}
export class BibtexCollector{
    async fromArxiv(query: string): Promise<CollectRes>{
        let _id = query.toLowerCase();
        if (_id.startsWith("arxiv:")){
            _id = _id.split("arxiv:")[1];
        }
        else if (_id.includes("arxiv.org/abs/")){
            _id = _id.split("arxiv.org/abs/")[1];
        }
        else if (_id.includes("arxiv.org/pdf/")){
            _id = _id.split("arxiv.org/pdf/")[1].split(".pdf")[0];
        }
        const paper = await fetchArxivPaperByID(_id);
        return {
            bibtex: bibtexFromArxiv(paper),
            url: paper.link
        }
    }
    async fromWebpage(url: string): Promise<CollectRes>{
        // Fetch webpage content
        // const response = await fetch(url, { method: 'GET', });
        const response = await fetch(`https://api.allorigins.win/get?url=${encodeURIComponent(url)}`);
        const htmlData = await response.text();
        // Parse webpage content
        const parser = new DOMParser();
        const doc = parser.parseFromString(htmlData, "text/html");
        // Get title
        const title = doc.querySelector("title")?.innerText;
        const bibtex = `@misc{${url},
            author = {},
            title = {${title}},
            url = {${url}},
            year = {${new Date().getFullYear()}},
            }`.replace(/  /g, "");
        return {
            bibtex: bibtex,
            url: url
        }
    };
}