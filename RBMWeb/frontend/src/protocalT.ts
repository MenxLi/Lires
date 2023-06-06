
export interface DataInfoT {
    has_file: boolean;
    file_type: string;
    year: string;
    title: string;
    author: string;
    authors: string[];
    tags: string[];
    uuid: string;
    url: string;
    time_added: number;
    time_modified: number;

    bibtex: string;
    doc_size: number;
    base_name: string;
}
