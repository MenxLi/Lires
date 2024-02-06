import { fetchArxivPaperByID, bibtexFromArxiv } from "../../utils/arxiv";

export type BibtexTypes = 'article' | 'inproceedings' | 'webpage' | 'misc';
export const getBibtexTemplate = (type: BibtexTypes, {
    entry = "",
    title = "",
    authors = [""],
    year = new Date().getFullYear(),
} = {}) => {
    if (!entry){
        // generate a random bibtex entry
        entry = `${year}_${Math.random().toString(36).substring(7)}`;
    }
    if (type == "article"){
        return `@article{${entry},
        author = {${authors.join(" and ")}},
        title = {${title}},
        journal = {},
        year = {${year}},
        abstract = {},
        volume = {},
        number = {},
        pages = {},
        month = {},
        doi = {},
        }`.replace(/  /g, "");
    }
    else if (type == "inproceedings"){
        return `@inproceedings{${entry},
        author = {${authors.join(" and ")},
        title = {${title}},
        booktitle = {},
        year = {${year}},
        abstract = {},
        editor = {},
        volume = {},
        number = {},
        series = {},
        pages = {},
        }`.replace(/  /g, "");
    }
    else if (type == "webpage"){
        return `@misc{${entry},
        title = "{${title}}",
        author = "{${authors.join(" and ")}}",
        year = {${year}},
        url = "{}",
        note = "{}"
        }`.replace(/  /g, "");

    }
    else if (type == "misc"){
        return `@misc{${entry},
        author = {${authors.join(" and ")}},
        title = {${title}},
        year = {${year}},
        url = {},
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
    static async fromArxiv(query: string): Promise<CollectRes>{
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
    static async fromWebpage(url: string): Promise<CollectRes>{
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
    static async fromDoi(doi: string): Promise<CollectRes>{
        const url = `https://api.crossref.org/works/${doi}/transform/application/x-bibtex`;
        const response = await fetch(url, { method: 'GET', });
        const bibtex = await response.text();
        return {
            bibtex: bibtex,
            url: `https://doi.org/${doi}`
        }
    }
}