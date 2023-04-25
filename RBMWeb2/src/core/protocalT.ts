
export interface DataInfoT {
    has_file: boolean;
    file_status: string;
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

    note_linecount: number;
}

export interface AccountPermission {
    is_admin: boolean;
    mandatory_tags: string[];
}