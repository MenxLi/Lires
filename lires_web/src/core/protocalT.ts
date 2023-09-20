
export interface DataInfoT {
    has_file: boolean;
    file_type: string;
    year: string;
    title: string;
    author: string;
    authors: string[];
    publication: string|null;
    tags: string[];
    uuid: string;
    url: string;
    time_added: number;
    time_modified: number;

    bibtex: string;
    doc_size: number;

    note_linecount: number;
    has_abstract: boolean;
}

export interface AccountPermission {
    is_admin: boolean;
    mandatory_tags: string[];
    identifier: string;
    enc_key: string;
}

export interface SearchResultant {
    score: number | null;
    match: null;
}

export type SearchResult = Record<string, SearchResultant | null>;
export type Changelog = [string, string[] | Record<string, string[]>][];