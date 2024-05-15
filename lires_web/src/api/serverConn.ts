
// Server connection

import type { DataInfoT, FeedDataInfoT, UserInfo, SearchType, SearchResult, Changelog, ServerStatus, DatabaseFeature, DatabaseUsage} from "./protocol.js";
import { sha256 } from "../utils/sha256lib";
import Fetcher from "./fetcher";

/**
 * Resolve the path of the resources on the server, 
 * these resources are the files that can be accessed by the get request.
 * NOT USED IN THE CURRENT VERSION
 */
export class HTTPPathResolver {
    constructor(private baseURLGetter: ()=>string, private tokenGetter: ()=>string = ()=>"" ){}
    public get baseURL(){ return this.baseURLGetter(); }
    public get token(){ return this.tokenGetter(); }

    doc(uid: string, userID: number): string{ return `${this.baseURL}/doc/${uid}?_u=${userID}`; }
    docDry = (uid: string, userID: number) => this.doc(uid, userID).replace("/doc/", "/doc-dry/");
    docText = (uid: string, userID: number) => this.doc(uid, userID).replace("/doc/", "/doc-text/");
    databaseDownload(data=false): string{ return `${this.baseURL}/api/database/download?data=${data}&key=${this.token}`; }
    miscFile(uid: string, fname: string): string{
        const encodedFname = encodeURIComponent(fname);
        return `${this.baseURL}/misc/${uid}?fname=${encodedFname}`;
    }

    userAvatar(username: string, opt: {
        size: number, 
        t: number | null
    } = { size: 128, t: -1 }): string{
        let tStamp;
        if(opt.t === null){ tStamp = ''; }
        else if (opt.t < 0){ tStamp = `&t=${Date.now()}`; }
        else{ tStamp = `&t=${opt.t}`; }
        return `${this.baseURL}/user-avatar/${username}?size=${opt.size}${tStamp}`
    }
}

/**
 * Properties:
 *  - resolve: resolve the path of the resources on the server  
 * 
 * Naming convention:
 *  - req...: request data from server
 *  - update...: update data on the server
 *  - delete...: delete data on the server
 *  - upload...: upload files
 *  - [Other]: functional methods that do not fit the above categories
 */
export class ServerConn {

    declare public fetcher: Fetcher;
    declare public resolve: HTTPPathResolver;
    constructor(baseUrlGetter: ()=>string, tokenGetter: ()=>string, sessionIDGetter: (()=>string) | null = null){
        if (sessionIDGetter === null){
            const _sessionID = Math.random().toString(36).substring(2);
            sessionIDGetter = () => _sessionID;
        }
        this.fetcher = new Fetcher({
            baseUrlGetter: baseUrlGetter,
            tokenGetter: tokenGetter,
            sessionIDGetter: sessionIDGetter,
        });
        this.resolve = new HTTPPathResolver(baseUrlGetter, tokenGetter);
    }
    public get baseURL(){ return this.fetcher.baseUrl; }
    async authorize(): Promise<UserInfo>{
        return await this.fetcher.post(`/api/auth`).then(res=>res.json());
    }

    async status(): Promise<ServerStatus>{
        return await this.fetcher.get(`/api/status`).then(res=>res.json());
    }
    
    async reqAllKeys(): Promise<string[]>{
        return await this.fetcher.get(`/api/database/keys`).then(res=>res.json());
    };
    async reqAllTags(): Promise<string[]>{
        return await this.fetcher.get(`/api/database/tags`).then(res=>res.json());
    };

    async reqDatabaseFeatureTSNE(collectionName = "doc_feature", nComponent = 3, perplexity = 10): Promise<DatabaseFeature>{
        return await this.fetcher.get(`/api/datafeat/tsne/${collectionName}`, {
            n_component: nComponent.toString(),
            perplexity: perplexity.toString(),
        }).then(res=>res.json());
    }

    async reqDatabaseUsage(): Promise<DatabaseUsage>{
        return await this.fetcher.get(`/api/database/usage`).then(res=>res.json());
    }

    async reqDatapointSummary( uid: string ): Promise<DataInfoT>{
        return await this.fetcher.get(`/api/datainfo/${uid}`).then(res=>res.json());
    }
    async reqDatapointSummaries( uids: string[] ): Promise<DataInfoT[]>{
        return await this.fetcher.post(`/api/datainfo-list`, {
            uids: JSON.stringify(uids),
        }).then(res=>res.json());
    }

    async deleteDatapoint(uid: string): Promise<boolean>{
        return await this.fetcher.post(`/api/dataman/delete`, {
            uuid: uid,
        }).then(()=>true);
    }

    /**
        * Create or update a datapoint
        * @param uid: the uid of the datapoint to update, if null, create a new datapoint
        * @param bibtex: the bibtex content
        * @param tags: the tags of the datapoint
        * @param url: the url of the datapoint
        * @return the updated datapoint
    */
    async updateDatapoint(
        uid: string | null, 
        {
            bibtex = null, 
            tags = null, 
            url = null,
        }: {
            bibtex?: string | null,
            tags?: string[] | null,
            url?: string | null,
        }
        ): Promise<DataInfoT>{
        if (!uid){
            // make sure other fields are not null
            if (bibtex === null || tags === null || url === null){
                throw new Error("uid is null, other fields should be complete");
            }
        }
        const params = {} as Record<string, any>;
        if (uid !== null) params["uuid"] = uid;
        if (bibtex !== null ) params["bibtex"] = bibtex;
        if (tags !== null) params["tags"] = JSON.stringify(tags);
        if (url !== null) params["url"] = url;
        return await this.fetcher.post(`/api/dataman/update`, params).then(res=>res.json());
    }

    async reqDatapointAbstract(uid: string): Promise<string>{
        return await this.fetcher.get(`/api/datainfo-supp/abstract/${uid}`).then(res=>res.text());
    }

    async updateDatapointAbstract(uid: string, content: string): Promise<boolean>{
        return await this.fetcher.post(`/api/datainfo-supp/abstract-update/${uid}`, {
            content: content,
        }).then((_) => true);
    }

    async reqDatapointNote( uid: string ): Promise<string>{
        return await this.fetcher.get(`/api/datainfo-supp/note/${uid}`).then(res=>res.text());
    }

    async updateDatapointNote( uid: string, content: string ): Promise<boolean>{
        return await this.fetcher.post(`/api/datainfo-supp/note-update/${uid}`, {
            content: content,
        }).then((_) => true);
        
    }

    async query({
        tags = [],
        searchBy = "title", 
        searchContent = "", 
        maxResults = 9999,
    }: {
        tags?: string[],
        searchBy?: SearchType,
        searchContent?: string,
        maxResults?: number,
    } = {}): Promise<SearchResult>{
        return await this.fetcher.post(`/api/filter/basic`, {
            tags: tags,
            search_by: searchBy,
            search_content: searchContent,
            top_k: maxResults,
        }).then(res=>res.json());
    }

    // =============================================
    //                 AI API              
    // =============================================

    async featurizeText(text: string, requireCache: boolean = false): Promise<number[]>{
        return await this.fetcher.post(`/api/iserver/textFeature`, {
            text: text,
            require_cache: requireCache,
        }).then(res=>res.json());
    }

    reqAISummary(
        uid: string, 
        onStreamComing: (txt: string)=>void, 
        onDone: ()=>void = ()=>{},
        force: boolean = true,
        model = "DEFAULT"
        ): void{
        this.fetcher.post(`/api/summary`, {
            force: force,
            uuid: uid,
            model: model,
        }).then(response => {
            if (!response.ok) {
                onStreamComing("(Error: " + response.status + ")");
                throw new Error("HTTP error " + response.status);
            }

            const reader = response.body!.getReader();
            const processTextData = ({ value, done } : {value: Uint8Array, done: boolean}) => {
                // Check if there is more data to process
                if (done) {
                    // All data has been processed
                    onDone();
                    return;
                }
                // Convert the received chunk (Uint8Array) to text
                let chunkText = new TextDecoder().decode(value);
                // appropriately treat the new-line characters
                // chunkText = chunkText.replace(/\n/g, "<br>");
                // Append the text to the content in the web page
                onStreamComing(chunkText);
                // Continue reading the next chunk
                return reader.read().then(processTextData as any);
            };
            return reader.read().then(processTextData as any);
        })
    }

    async reqMiscFileList(uid: string): Promise<string[]>{
        return await this.fetcher.get(`/api/misc-list/${uid}`).then(res=>res.json());
    }
    async deleteMiscFile(uid: string, fileName: string): Promise<boolean>{
        return await this.fetcher.delete(`/misc/${uid}`, {
            'fname': fileName,
        }).then(()=>true);
    }
    async renameMiscFile(uid: string, fileName: string, newFileName: string): Promise<boolean>{
        return await this.fetcher.post(`/misc/${uid}`, {
            'fname': fileName,
            'dst_fname': newFileName,
        }).then(()=>true);
    }

    /* upload files to the misc folder and return the file names */
    async uploadMiscFiles(uid: string, files: File[]): Promise<string[]>{
        const res = await Promise.all(
            files.map((file) => {
                // file is an object of File class: https://developer.mozilla.org/en-US/docs/Web/API/File
                return new Promise((resolve, reject) => {
                    this.fetcher.put(`/misc/${uid}`, file)
                        .then(res=>res.json())
                        .then(resolve)
                        .catch(reject);
                });
            })
        );
        return res.map((r: any) => r.file_name);
    }

    /* upload document and return the new datapoint summary */
    async uploadDocument(uid: string, file: File): Promise<DataInfoT>{
        return await this.fetcher.put(`/doc/${uid}`, file).then(res=>res.json());
    }

    /* free document and return the new datapoint summary */
    async deleteDocument(uid: string): Promise<DataInfoT>{
        return await this.fetcher.delete(`/doc/${uid}`).then(res=>res.json());
    }

    /* rename tag for all datapoints */
    async updateTagAll(oldTag: string, newTag: string): Promise<boolean>{
        return await this.fetcher.post(`/api/database/tag-rename`, {
            oldTag: oldTag,
            newTag: newTag,
        }).then(()=>true);
    }

    /* delete tag for all datapoints */
    async deleteTagAll(tag: string): Promise<boolean>{
        return await this.fetcher.post(`/api/database/tag-delete`, {
            tag: tag,
        }).then(()=>true);
    }

    // =============================================
    //                User related               
    // =============================================

    async reqUserInfo(username: string): Promise<UserInfo>{
        // TODO: use get
        return await this.fetcher.post(`/api/user/info/${username}`).then(res=>res.json());
    }

    async updateUserNickname(name: string): Promise<UserInfo>{
        // the user is identified by the key
        return await this.fetcher.post(`/api/user/info-update`, {
            name: name,
        }).then(res=>res.json());
    }

    async updateUserPassword(newPassword: string): Promise<UserInfo>{
        // the user is identified by the key
        return await this.fetcher.post(`/api/user/info-update`, {
            password: sha256(newPassword),
        }).then(res=>res.json());
    }

    async reqUserList(): Promise<UserInfo[]>{
        return await this.fetcher.post(`/api/user/list`, {}).then(res=>res.json());
    }

    async uploadUserAvatar(username: string, file: File): Promise<UserInfo>{
        return await this.fetcher.put(`/user-avatar/${username}`, file).then(res=>res.json());
    }

    // User management
    async updateUserAccess(username: string, setAdmin: boolean | null, setMandatoryTags: string[] | null, max_storage: number | null): Promise<UserInfo>{
        const formObj = {} as Record<string, any>;
        formObj.username = username;
        if (setAdmin !== null) 
            formObj.is_admin = setAdmin.toString();
        if (setMandatoryTags !== null) 
            formObj.mandatory_tags = JSON.stringify(setMandatoryTags);
        if (max_storage !== null) 
            formObj.max_storage = max_storage;
        return await this.fetcher.post(`/api/userman/modify`, formObj).then(res=>res.json());
    }

    async registerUser(invitation_code: string, username: string, password: string, name: string): Promise<UserInfo>{
        return await this.fetcher.post(`/api/userman/register`, {
            invitation_code,
            username,
            password: sha256(password),
            name
        }).then(res=>res.json())
    }

    async createUser(username: string, name: string, password: string, isAdmin: boolean, mandatoryTags: string[], max_storage: number): Promise<UserInfo>{
        return await this.fetcher.post(`/api/userman/create`, {
            username: username,
            name: name,
            password: sha256(password),
            is_admin: isAdmin.toString(),
            mandatory_tags: JSON.stringify(mandatoryTags),
            max_storage: max_storage,
        }).then(res=>res.json());
    }

    async deleteUser(username: string){
        return await this.fetcher.post(`/api/userman/delete`, {
            username: username,
        }).then(()=>true);
    }

    // =============================================
    //                 Feed              
    // =============================================
    async reqFeedList({
        maxResults = 10,
        category = "",
        timeBefore = -1,
        timeAfter = -1,
    }:{
        maxResults?: number,
        category?: string,
        timeBefore?: number,
        timeAfter?: number,
    }): Promise<FeedDataInfoT[]>{
        console.log("reqFeedList", maxResults, category, timeBefore, timeAfter);
        return await this.fetcher.post(`/api/feed/query`, {
            max_results: maxResults,
            category: category,
            time_before: timeBefore,
            time_after: timeAfter,
        }).then(res=>res.json());
    }

    async reqFeedCategories(): Promise<string[]>{
        return await this.fetcher.get(`/api/feed/categories`).then(res=>res.json());
    }

    // ---- info ----
    async changelog(): Promise<Changelog>{
        return await this.fetcher.get(`/api/info/changelog`).then(res=>res.json());
    }
}

export default ServerConn;