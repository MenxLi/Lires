
export interface ServerStatus {
    status: 'OK';
    n_data: number;
    uptime: number;
}

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

export type DatabaseFeature = Record<string, number[]>;

export interface UserInfo {
    id: number;
    username: string;
    enc_key: string;
    name: string;
    is_admin: boolean;
    mandatory_tags: string[];
    has_avatar: boolean;
}

export interface SearchResultant {
    score: number | null;
    match: null;
}

export type SearchResult = Record<string, SearchResultant | null>;
export type Changelog = [string, string[] | Record<string, string[]>][];