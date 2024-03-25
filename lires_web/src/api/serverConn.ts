
// Server connection

import type { DataInfoT, FeedDataInfoT, UserInfo, SearchResult, SearchResult2, Changelog, ServerStatus, DatabaseFeature, DatabaseUsage} from "./protocol.js";
import { sha256 } from "../utils/sha256lib";
import Fetcher from "./fetcher";

export class ServerConn {
    declare fetcher: Fetcher;
    constructor(baseUrlGetter: ()=>string, tokenGetter: ()=>string, sessionIDGetter: ()=>string){
        this.fetcher = new Fetcher({
            baseUrlGetter: baseUrlGetter,
            tokenGetter: tokenGetter,
            sessionIDGetter: sessionIDGetter,
        });
    }
    public get baseURL(){ return this.fetcher.baseUrl; }
    async authUsr( encKey: string ): Promise<UserInfo>{
        return await this.fetcher.post(`/api/auth`, {
            key: encKey,
        }).then(res=>res.json());
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

    async reqDatapointAbstract(uid: string): Promise<string>{
        return await this.fetcher.get(`/api/datainfo-supp/abstract/${uid}`).then(res=>res.text());
    }

    async reqDatapointAbstractUpdate(uid: string, content: string): Promise<boolean>{
        return await this.fetcher.post(`/api/datainfo-supp/abstract-update/${uid}`, {
            content: content,
        }).then((_) => true);
    }

    async reqDatapointNote( uid: string ): Promise<string>{
        return await this.fetcher.get(`/api/datainfo-supp/note/${uid}`).then(res=>res.text());
    }

    async reqDatapointNoteUpdate( uid: string, content: string ): Promise<boolean>{
        return await this.fetcher.post(`/api/datainfo-supp/note-update/${uid}`, {
            content: content,
        }).then((_) => true);
        
    }

    async search(method: string, kwargs: any): Promise<SearchResult>{
        return await this.fetcher.post(`/api/search`, {
            method: method,
            kwargs: JSON.stringify(kwargs),
        }).then(res=>res.json());
    }

    async filter({
        tags = [],
        searchBy = "title", 
        searchContent = "", 
        max_results = 9999,
    }: {
        tags?: string[],
        searchBy?: string,
        searchContent?: string,
        max_results?: number,
    } = {}): Promise<SearchResult2>{
        return await this.fetcher.post(`/api/filter/basic`, {
            tags: tags,
            search_by: searchBy,
            search_content: searchContent,
            top_k: max_results,
        }).then(res=>res.json());
    }

    // =============================================
    //                 AI API              
    // =============================================

    async featurize(text: string, requireCache: boolean = false): Promise<number[]>{
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

    // =============================================
    //                Manipulate data               
    // =============================================

    async deleteData(uid: string): Promise<boolean>{
        return await this.fetcher.post(`/api/dataman/delete`, {
            uuid: uid,
        }).then(()=>true);
    }
    
    async editData(
        uid: string | null, 
        bibtex: string | null = null, 
        tags: string[] | null = null, 
        url: string | null = null,
        ): Promise<DataInfoT>{
        if (!uid){
            // make sure other fields are not null
            if (bibtex === null || tags === null || url === null){
                throw new Error("uid is null, other fields should be complete");
            }
        }
        const params = {} as Record<string, any>;
        if (uid !== null) params["uuid"] = JSON.stringify(uid);
        if (bibtex !== null ) params["bibtex"] = bibtex;
        if (tags !== null) params["tags"] = JSON.stringify(tags);
        if (url !== null) params["url"] = url;
        return await this.fetcher.post(`/api/dataman/update`, params).then(res=>res.json());
    }

    async listMiscFiles(uid: string): Promise<string[]>{
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
    async freeDocument(uid: string): Promise<DataInfoT>{
        return await this.fetcher.delete(`/doc/${uid}`).then(res=>res.json());
    }

    async renameTag(oldTag: string, newTag: string): Promise<boolean>{
        return await this.fetcher.post(`/api/dataman/tag-rename`, {
            oldTag: oldTag,
            newTag: newTag,
        }).then(()=>true);
    }

    async deleteTag(tag: string): Promise<boolean>{
        return await this.fetcher.post(`/api/dataman/tag-delete`, {
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
    async setUserAccess(username: string, setAdmin: boolean | null, setMandatoryTags: string[] | null, max_storage: number | null): Promise<UserInfo>{
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
    async fetchFeedList(maxResults = 10, category="arxiv"): Promise<FeedDataInfoT[]>{
        return await this.fetcher.post(`/api/feed`, {
            max_results: maxResults,
            category: category,
        }).then(res=>res.json());
    }

    // ---- info ----
    async changelog(): Promise<Changelog>{
        return await this.fetcher.get(`/api/info/changelog`).then(res=>res.json());
    }
}

export default ServerConn;