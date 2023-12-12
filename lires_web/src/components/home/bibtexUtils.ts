
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