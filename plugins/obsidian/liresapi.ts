import Fetcher from "./fetcher";
import type { DataInfoT, UserInfo } from "../../lires_web/src/api/protocol";

const _dummyDataSummary: DataInfoT = {
    has_file : false,
    file_type: "",
    year: "0000",
    title: " ",
    author: " ",
    authors: [" "],
    publication: null,
    tags: [],
    uuid: " ",
    url: "about:blank",
    time_added: 0.,
    time_modified: 0.,
    bibtex: "",
    doc_size: 0,
    note_linecount: 0,
    has_abstract: false,
}

export default class LiresAPI {

    _fetcher: Fetcher;
    _endpointGetter: () => string;
    _credentialGetter: () => string;

    constructor() {}

    public init(endpointGetter: () => string, credentialGetter: () => string): LiresAPI {
        const __thisSessionId = Math.random().toString(36).substring(2, 15);
        this._fetcher = new Fetcher(
            {
                'baseUrlGetter': endpointGetter,
                'tokenGetter': credentialGetter,
                'sessionIDGetter': ()=>{return 'obsidian-'+__thisSessionId;}
            }
        );
        return this;
    }

    async reqUserInfo(): Promise<UserInfo>{
        return await this._fetcher.post('/api/auth').then(res=>res.json());
    }

    async reqDatapointSummary( uid: string ): Promise<DataInfoT>{
        try{
            return await this._fetcher.get(`/api/datainfo/${uid}`).then(res=>res.json());
        }
        catch(e){
            console.log(e);
            return _dummyDataSummary;
        }
    }

    async reqDatapointAbstract( uid: string ): Promise<string>{
        return await this._fetcher.get(`/api/datainfo-supp/abstract/${uid}`).then(res=>res.text());
    }

    async reqDatapointNote( uid: string ): Promise<string>{
        return await this._fetcher.get(`/api/datainfo-supp/note/${uid}`).then(res=>res.text());
    }

    parseMarkdown = (
        backend: string, 
        content: string, 
        dpSummary: DataInfoT, 
        user: UserInfo) => {
        content = content.replace(
            new RegExp('./misc/', 'g'), 
            `${backend}/misc/${dpSummary.uuid}?_u=${user.id}&&fname=`
            );
        return content;
    }
}
