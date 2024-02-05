
// Server connection

import {getBackendURL} from "../config.js";
import { useSettingsStore } from "../components/store.js";
import type { DataInfoT, UserInfo, SearchResult, Changelog, ServerStatus, DatabaseFeature} from "./protocalT.js";
import { sha256 } from "../utils/sha256lib.js";
import Fetcher from "./fetcher.js";

export class ServerConn {
    declare fetcher: Fetcher;
    constructor(){
        this.fetcher = new Fetcher();
        this.fetcher.setBaseUrlGetter(()=>`${getBackendURL()}`)
        this.fetcher.setCredentialGetter(()=>useSettingsStore().encKey);
    }
    get settings(){
        return useSettingsStore();
    }
    apiURL(){
        return getBackendURL() + "/api";
    }
    async authUsr( encKey: string ): Promise<UserInfo>{
        return await this.fetcher.post(`/api/auth`, {
            key: encKey,
        }).then(res=>res.json());
    }

    async status(): Promise<ServerStatus>{
        return await this.fetcher.get(`/api/status`).then(res=>res.json());
    }
    
    async reqFileList( tags: string[] ): Promise<DataInfoT[]>{
        return await this.fetcher.get(`/api/filelist`,
            { tags: tags.join("&&"), }
        ).then(res=>res.json());
    };

    // get the file list in a streaming way
    async reqFileListStream( 
        tags: string[] = [],
        onReceive: (data_: DataInfoT, nCurrent_: number, nTotal_: number)=>void = ()=>{},
        ){

        const response = await this.fetcher.get(`/api/filelist-stream`, {
            tags: tags.join("&&"),
        });

        const _nTotal = response.headers.get("totalDataCount");
        const nTotal = _nTotal?parseInt(_nTotal):-1;
        let nCurrent = 0;

        const reader = response.body!.getReader();
        let partialData = "";
        const processTextData = ({ value, done } : {value: Uint8Array, done: boolean}) => {
            
            const chunkText = partialData + new TextDecoder().decode(value);

            // Split the chunk into individual JSON strings
            const jsonStrings = chunkText.split("\\N");

            // Process each JSON string, except the last one
            for (let i = 0; i < jsonStrings.length - 1; i++) {
                const jsonString = jsonStrings[i];
                try{
                    const data = JSON.parse(jsonString) as DataInfoT;
                    nCurrent += 1;
                    onReceive(data, nCurrent, nTotal);
                }
                catch(err){
                    // incomplete JSON string, should not happen
                    console.error(err);
                }
            }
            // Store the partial data from the last JSON string in the chunk
            if (jsonStrings.length > 0){
                partialData = jsonStrings[jsonStrings.length - 1];
            }
            if (done) {
                if (partialData) {
                    try{
                        const data = JSON.parse(partialData) as DataInfoT;
                        nCurrent += 1;
                        onReceive(data, nCurrent, nTotal);
                    }
                    catch(err){
                        // the last chunk should contain an entire JSON string
                        // incomplete JSON string, should not happen
                        console.error(err);
                    }
                }
                return;
            }
            return reader.read().then(processTextData as any);
        }
        return reader.read().then(processTextData as any);
    }

    async reqDatabaseFeatureTSNE(collectionName = "doc_feature", nComponent = 3, perplexity = 10): Promise<DatabaseFeature>{
        return await this.fetcher.get(`/api/datafeat/tsne/${collectionName}`, {
            n_component: nComponent.toString(),
            perplexity: perplexity.toString(),
        }).then(res=>res.json());
    }

    async reqDatapointSummary( uid: string ): Promise<DataInfoT>{
        return await this.fetcher.get(`/api/fileinfo/${uid}`).then(res=>res.json());
    }

    async reqReloadDB(): Promise<boolean>{
        return await this.fetcher.post(`/api/reload-db`).then(_=>true);
    }

    async reqDatapointAbstract(uid: string): Promise<string>{
        return await this.fetcher.get(`/api/fileinfo-supp/abstract/${uid}`).then(res=>res.text());
    }

    async reqDatapointAbstractUpdate(uid: string, content: string): Promise<boolean>{
        return await this.fetcher.post(`/api/fileinfo-supp/abstract-update/${uid}`, {
            content: content,
        }).then((_) => true);
    }

    async reqDatapointNote( uid: string ): Promise<string>{
        return await this.fetcher.get(`/api/fileinfo-supp/note/${uid}`).then(res=>res.text());
    }

    async reqDatapointNoteUpdate( uid: string, content: string ): Promise<boolean>{
        return await this.fetcher.post(`/api/fileinfo-supp/note-update/${uid}`, {
            content: content,
        }).then((_) => true);
        
    }

    async search(method: string, kwargs: any): Promise<SearchResult>{
        return await this.fetcher.post(`/api/search`, {
            method: method,
            kwargs: JSON.stringify(kwargs),
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

    /* upload images to the misc folder and return the file names */
    async uploadImages(uid: string, files: File[]): Promise<string[]>{
        const res = await Promise.all(
            files.map((file) => {
                // file is an object of File class: https://developer.mozilla.org/en-US/docs/Web/API/File
                return new Promise((resolve, reject) => {
                    this.fetcher.put(`/img/${uid}`, file)
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
    async setUserAccess(username: string, setAdmin: boolean | null, setMandatoryTags: string[] | null): Promise<UserInfo>{
        const formObj = {} as Record<string, any>;
        formObj.username = username;
        if (setAdmin !== null) 
            formObj.is_admin = setAdmin.toString();
        if (setMandatoryTags !== null) 
            formObj.mandatory_tags = JSON.stringify(setMandatoryTags);
        return await this.fetcher.post(`/api/userman/modify`, formObj).then(res=>res.json());
    }

    async createUser(username: string, name: string, password: string, isAdmin: boolean, mandatoryTags: string[]): Promise<UserInfo>{
        return await this.fetcher.post(`/api/userman/create`, {
            username: username,
            name: name,
            password: sha256(password),
            is_admin: isAdmin.toString(),
            mandatory_tags: JSON.stringify(mandatoryTags),
        }).then(res=>res.json());
    }

    async deleteUser(username: string){
        return await this.fetcher.post(`/api/userman/delete`, {
            username: username,
        }).then(()=>true);
    }

    // ---- info ----
    async changelog(): Promise<Changelog>{
        return await this.fetcher.get(`/api/info/changelog`).then(res=>res.json());
    }
}