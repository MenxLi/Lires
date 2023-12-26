
// Server connection

import {getBackendURL} from "../config.js";
import { useSettingsStore } from "../components/store.js";
import type { DataInfoT, UserInfo, SearchResult, Changelog, ServerStatus, DatabaseFeature} from "./protocalT.js";
import { sha256 } from "../libs/sha256lib.js";

export class ServerConn {
    constructor(){
        // this.settings = useSettingsStore();
    }
    get settings(){
        return useSettingsStore();
    }
    apiURL(){
        return getBackendURL();
    }
    async authUsr( encKey: string ): Promise<UserInfo>{
            const params = new URLSearchParams();
            params.set("key", encKey);

            const response = await fetch(`${getBackendURL()}/auth`, 
                {
                    method: "POST",
                    headers: {
                        "Content-Type":"application/x-www-form-urlencoded"
                    },
                    body: params.toString()
                })
            if (response.ok && response.status === 200) {
                return JSON.parse(await response.text());
            }
            else{
                throw new Error(`Got response: ${response.status}`);
            }
    }

    async status(): Promise<ServerStatus>{
        const form = new FormData();
        form.append('key', this.settings.encKey);

        const response = await fetch(`${getBackendURL()}/status`, {
            method: 'POST',
            body: form,
        });
        console.log(response);
        if (response.ok){
            return JSON.parse(await response.text());
        }
        else{
            throw new Error(`Got response: ${response.status}`)
        }
    }
    
    async reqFileList( tags: string[] ): Promise<DataInfoT[]>{
        const concatTags = tags.join("&&");
        const url = new URL(`${getBackendURL()}/filelist`);
        url.searchParams.append("tags", concatTags);
        url.searchParams.append("key", this.settings.encKey);

        const response = await fetch(url.toString());
        if (response.ok){
            const resObj = await response.json();
            const DataInfoList: DataInfoT[] = resObj;
            return DataInfoList;
        }
        else {
            throw new Error(`Got response: ${response.status}`)
        }
    };

    // get the file list in a streaming way
    async reqFileListStream( 
        tags: string[] = [],
        onReceive: (data_: DataInfoT, nCurrent_: number, nTotal_: number)=>void = ()=>{},
        ){

        const concatTags = tags.join("&&");
        const url = new URL(`${getBackendURL()}/filelist-stream`);
        url.searchParams.append("tags", concatTags);
        url.searchParams.append("key", this.settings.encKey);

        const response = await fetch(url.toString());
        if (!response.ok){
            throw new Error(`Got response: ${response.status}`)
        };

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
        const url = new URL(`${getBackendURL()}/datafeat/tsne/${collectionName}`);
        url.searchParams.append("key", this.settings.encKey);
        url.searchParams.append("n_component", nComponent.toString());
        url.searchParams.append("perplexity", perplexity.toString());
        // url.searchParams.append("random_state", Math.floor(Math.random()*1000).toString());

        const response = await fetch(url.toString());
        if (response.ok){
            const resObj = await response.json();
            const DataFeatList: DatabaseFeature = resObj;
            return DataFeatList;
        }
        else{
            throw new Error(`Got response: ${response.status}`)
        }
    }

    async reqDatapointSummary( uid: string ): Promise<DataInfoT>{
        const url = new URL(`${getBackendURL()}/fileinfo/${uid}`);
        url.searchParams.append("key", this.settings.encKey);

        const response = await fetch(url.toString());
        if (response.ok){
            const resObj = await response.json();
            const DataInfo: DataInfoT = resObj;
            return DataInfo;
        }
        else {
            throw new Error(`Got response: ${response.status}`)
        }
    }

    async reqReloadDB(): Promise<boolean>{
        const form = new FormData();
        form.append('key', this.settings.encKey)
        const res = await fetch(`${getBackendURL()}/reload-db`, {
            method: 'POST',
            body: form,
        });
        if (res.ok){
            return true;
        }
        else{
            throw new Error(`Got response: ${res.status}`)
        }
    }

    async reqDatapointAbstract(uid: string): Promise<string>{
        const params = new URLSearchParams();
        params.set("key", this.settings.encKey);
        const response = await fetch(`${getBackendURL()}/fileinfo-supp/abstract/${uid}`);
        if (response.ok && response.status === 200) {
            const res: string = await response.text();
            return res
        }
        else{
            throw new Error(`Got response: ${response.status}`);
        }
    }

    async reqDatapointAbstractUpdate(uid: string, content: string): Promise<boolean>{
        const form = new FormData();
        form.append('key', this.settings.encKey)
        form.append('content', content)
        const res = await fetch(`${getBackendURL()}/fileinfo-supp/abstract-update/${uid}`, {
            method: 'POST',
            body: form,
        });
        if (res.ok){
            return true;
        }
        else{
            throw new Error(`Got response: ${res.status}`)
        }
    }

    async reqDatapointNote( uid: string ): Promise<string>{
        const url = new URL(`${getBackendURL()}/fileinfo-supp/note/${uid}`);
        url.searchParams.append("key", this.settings.encKey);
        const response = await fetch(url.toString());
        if (response.ok){
            const resObj = await response.text();
            return resObj;
        }
        else{
            throw new Error(`Got response: ${response.status}`)
        }
    }

    async reqDatapointNoteUpdate( uid: string, content: string ): Promise<boolean>{
        const url = new URL(`${getBackendURL()}/fileinfo-supp/note-update/${uid}`);
        url.searchParams.append("key", this.settings.encKey);
        url.searchParams.append("content", content);
        const response = await fetch(url.toString(),
            {
                method: "POST",
                headers: {
                    "Content-Type":"application/x-www-form-urlencoded"
                },
            }
        );
        if (response.ok){
            return true;
        }
        else{
            throw new Error(`Got response: ${response.status}`)
        }
    }

    async search(method: string, kwargs: any): Promise<SearchResult>{
        const params = new URLSearchParams();

        params.set("key", this.settings.encKey);
        params.set("method", method);
        params.set("kwargs", JSON.stringify(kwargs));
        const response = await fetch(`${getBackendURL()}/search`, 
            {
                method: "POST",
                headers: {
                    "Content-Type":"application/x-www-form-urlencoded"
                },
                body: params.toString(),
            })
        if (response.ok && response.status === 200) {
            const res: SearchResult = JSON.parse(await response.text());
            return res
        }
        else{
            throw new Error(`Got response: ${response.status}`);
        }

    }

    // =============================================
    //                 AI API              
    // =============================================

    async featurize(text: string, requireCache: boolean = false): Promise<number[]>{
        const params = new URLSearchParams();
        params.set("key", this.settings.encKey);
        params.set("text", text);
        params.set("require_cache", requireCache.toString());

        const response = await fetch(`${getBackendURL()}/iserver/textFeature?${params.toString()}`,
            {
                method: "POST",
                headers: {
                    "Content-Type":"application/x-www-form-urlencoded"
                },
            }
        );

        if (response.ok && response.status === 200) {
            const txt = await response.text();
            const res: number[] = JSON.parse(txt);
            return res
        }
        else{
            throw new Error(`Got response: ${response.status}`);
        }
    }

    reqAISummary(
        uid: string, 
        onStreamComing: (txt: string)=>void, 
        onDone: ()=>void = ()=>{},
        force: boolean = true,
        model = "DEFAULT"
        ): void{
        const form = new FormData();
        form.append('key', this.settings.encKey)
        form.append('force', force.toString())
        form.append('uuid', uid)
        form.append('model', model)
        const res = fetch(`${getBackendURL()}/summary`, {
            method: 'POST',
            body: form,
        })
        res.then(response => {
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
        }).catch(error => {
            console.error(error);
        })
    }

    // =============================================
    //                Manipulate data               
    // =============================================

    async deleteData(uid: string): Promise<boolean>{
        const url = new URL(`${getBackendURL()}/dataman/delete`);
        url.searchParams.append("key", this.settings.encKey);
        url.searchParams.append("uuid", uid);

        const response = await fetch(url.toString(),
            {
                method: "POST",
                headers: {
                    "Content-Type":"application/x-www-form-urlencoded"
                },
            }
        );
        if (response.ok && response.status === 200) {
            return true;
        } else {
            throw new Error(`Got response: ${response.status}`);
        }
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
        const params = new URLSearchParams();
        if (!uid){ uid = null; }
        params.set("key", this.settings.encKey);
        params.set("uuid", JSON.stringify(uid))
        if (bibtex !== null ) params.set("bibtex", bibtex);
        if (tags !== null) params.set("tags", JSON.stringify(tags));
        if (url !== null) params.set("url", url);
        const response = await fetch(`${getBackendURL()}/dataman/update`,
            {
                method: "POST",
                headers: {
                    "Content-Type":"application/x-www-form-urlencoded"
                },
                body: params.toString(),
            }
        );
        if (response.ok && response.status === 200) {
            const res: DataInfoT = JSON.parse(await response.text());
            return res
        }
        else{
            throw new Error(`Got response: ${response.status}`);
        }
    }

    /* upload images to the misc folder and return the file names */
    async uploadImages(uid: string, files: File[]): Promise<string[]>{
        const res = await Promise.all(
            files.map((file) => {
                // file is an object of File class: https://developer.mozilla.org/en-US/docs/Web/API/File
                return new Promise((resolve, reject) => {
                    const form = new FormData();
                    form.append('file', file);
                    form.append('key', this.settings.encKey)
                    
                    fetch(`${getBackendURL()}/img-upload/${uid}`, {
                        method: 'POST',
                        body: form,
                    })
                    .then((response) => {
                        if (!response.ok) {
                        throw new Error('Network response was not ok');
                        }
                        return response.json();
                    })
                    .then((data) => resolve(data))
                    .catch((error) => reject(error));
                });
            })
        );
        return res.map((r: any) => r.file_name);
    }

    /* upload document and return the new datapoint summary */
    async uploadDocument(uid: string, file: File): Promise<DataInfoT>{
        const form = new FormData();
        form.append('file', file);
        form.append('key', this.settings.encKey)
        const res = await fetch(`${getBackendURL()}/doc/${uid}`, {
            method: 'PUT',
            body: form,
        })
        if (res.ok){
            const resObj = await res.json();
            const DataInfo: DataInfoT = resObj;
            return DataInfo;
        }
        else{
            throw new Error(`Got response: ${res.status}`)
        }
    }

    /* free document and return the new datapoint summary */
    async freeDocument(uid: string): Promise<DataInfoT>{
        const form = new FormData();
        form.append('key', this.settings.encKey)
        const res = await fetch(`${getBackendURL()}/doc/${uid}`, {
            method: 'DELETE',
            body: form,
        });
        if (res.ok){
            const resObj = await res.json();
            const DataInfo: DataInfoT = resObj;
            return DataInfo;
        }
        else{
            throw new Error(`Got response: ${res.status}`)
        }
    }

    async renameTag(oldTag: string, newTag: string): Promise<boolean>{
        const form = new FormData();
        form.append('key', this.settings.encKey)
        form.append('oldTag', oldTag)
        form.append('newTag', newTag)

        const res = await fetch(`${getBackendURL()}/dataman/tag-rename`, {
            method: 'POST',
            body: form,
        });
        if (res.ok){ return true; }
        else{ throw new Error(`Got response: ${res.status}`) }
    }

    async deleteTag(tag: string): Promise<boolean>{
        const form = new FormData();
        form.append('key', this.settings.encKey)
        form.append('tag', tag)

        const res = await fetch(`${getBackendURL()}/dataman/tag-delete`, {
            method: 'POST',
            body: form,
        });
        if (res.ok){ return true; }
        else{ throw new Error(`Got response: ${res.status}`) }
    }

    // =============================================
    //                User related               
    // =============================================

    async reqUserInfo(username: string): Promise<UserInfo>{
        const form = new FormData();
        form.append('key', this.settings.encKey)

        const res = await fetch(`${getBackendURL()}/user/info/${username}`, {
            method: 'POST',
            body: form,
        });
        if (res.ok){ return await res.json(); }
        else { throw new Error(`Got response: ${res.status}`) }
    }

    async updateUserNickname(name: string): Promise<UserInfo>{
        const form = new FormData();
        form.append('key', this.settings.encKey) // the user is identified by the key
        form.append('name', name)

        const res = await fetch(`${getBackendURL()}/user/info-update`, {
            method: 'POST',
            body: form,
        });
        if (res.ok){ return await res.json(); }
        else { throw new Error(`Got response: ${res.status}`) }
    }

    async updateUserPassword(newPassword: string): Promise<UserInfo>{
        const form = new FormData();
        form.append('key', this.settings.encKey) // the user is identified by the key
        form.append('password', sha256(newPassword))
        
        const res = await fetch(`${getBackendURL()}/user/info-update`, {
            method: 'POST',
            body: form,
        });
        if (res.ok){ return await res.json(); }
        else { throw new Error(`Got response: ${res.status}`) }
    }

    async reqUserList(): Promise<UserInfo[]>{
        const form = new FormData();
        form.append('key', this.settings.encKey)

        const res = await fetch(`${getBackendURL()}/user/list`, {
            method: 'POST',
            body: form,
        });
        if (res.ok){ return await res.json(); }
        else { throw new Error(`Got response: ${res.status}`) }
    }

    async uploadUserAvatar(file: File): Promise<UserInfo>{
        const form = new FormData();
        form.append('file', file);
        form.append('key', this.settings.encKey)
        const res = await fetch(`${getBackendURL()}/user/avatar-upload`, {
            method: 'POST',
            body: form,
        })
        if (res.ok){ return await res.json(); }
        else { throw new Error(`Got response: ${res.status}`) }
    }

    async setUserAccess(username: string, setAdmin: boolean | null, setMandatoryTags: string[] | null): Promise<UserInfo>{
        const form = new FormData();
        form.append('key', this.settings.encKey)
        form.append('username', username)
        if (setAdmin !== null) form.append('is_admin', setAdmin.toString())
        if (setMandatoryTags !== null) form.append('mandatory_tags', JSON.stringify(setMandatoryTags))

        const res = await fetch(`${getBackendURL()}/userman/modify`, {
            method: 'POST',
            body: form,
        });
        if (res.ok){ return await res.json(); }
        else { throw new Error(`Got response: ${res.status}`) }
    }

    async createUser(username: string, name: string, password: string, isAdmin: boolean, mandatoryTags: string[]): Promise<UserInfo>{
        const form = new FormData();
        form.append('key', this.settings.encKey)
        form.append('username', username)
        form.append('name', name)
        form.append('password', sha256(password))
        form.append('is_admin', isAdmin.toString())
        form.append('mandatory_tags', JSON.stringify(mandatoryTags))

        const res = await fetch(`${getBackendURL()}/userman/create`, {
            method: 'POST',
            body: form,
        });
        if (res.ok){ return await res.json(); }
        else { throw new Error(`Got response: ${res.status}`) }
    }

    async deleteUser(username: string){
        const form = new FormData();
        form.append('key', this.settings.encKey)
        form.append('username', username)

        const res = await fetch(`${getBackendURL()}/userman/delete`, {
            method: 'POST',
            body: form,
        });
        if (res.ok){ return true; }
        else { throw new Error(`Got response: ${res.status}`) }
    }

    // ---- info ----
    async changelog(): Promise<Changelog>{
        const url = new URL(`${getBackendURL()}/info/changelog`);
        url.searchParams.append("key", this.settings.encKey);
        const response = await fetch(url.toString(),
            {
                method: "GET",
                headers: {
                    "Content-Type":"application/x-www-form-urlencoded"
                },
            }
        );
        if (response.ok && response.status === 200) {
            const res = JSON.parse(await response.text());
            return res;
        } else {
            throw new Error(`Got response: ${response.status}`);
        }
    }
}
