
export interface ServerStatus {
    status: 'online' | 'offline' | 'maintenance';
    version: string;
    n_data: number;
    n_connections: number;
    uptime: number;
}
export interface DatabaseUsage {
    n_entries: number;
    disk_usage: number; // in bytes
    disk_limit: number; // in bytes
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

export interface FeedDataInfoT extends DataInfoT {
    abstract: string;
    authors_other_publications: string[][];
    feature: number[];
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
    max_storage: number;
}

export interface SearchResultant {
    score: number | null;
    match: null;
}

export type SearchResult = Record<string, SearchResultant | null>;
export type Changelog = [string, string[] | Record<string, string[]>][];

export type SearchType = 'title' | 'author' | 'year' | 'note' | 'publication' | 'feature' | 'uuid';
export interface SearchResult2 {
    uids: string[];
    scores: number[] | null;
}



// Event for websocket to broadcast
interface EventBase{
    type: 
    'delete_entry' | 'add_entry' | 'update_entry' | 'update_note' |
    'delete_tag' | 'update_tag' |
    'delete_user' | 'add_user' | 'update_user' |
    'login' | 'logout';

    session_id: string;
}

export interface Event_Data extends EventBase{
    type: 'delete_entry' | 'add_entry' | 'update_entry'
    uuid: string;
    datapoint_summary: DataInfoT | null;
}

export interface Event_DataNote extends EventBase{
    type: 'update_note'
    note: string;
}

export interface Event_Tag extends EventBase{
    type: 'delete_tag' | 'update_tag'
    src_tag: string
    dst_tag: string | null
}

export interface Event_User extends EventBase{
    type: 'delete_user' | 'add_user' | 'update_user' | 'login' | 'logout'
    username: string;
    user_info: UserInfo | null
}

export type Event = Event_Data | Event_Tag | Event_User | Event_DataNote;