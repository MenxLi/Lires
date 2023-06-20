
// Server connection

import { getCookie } from "../libs/cookie.js";
import {getBackendURL} from "../config.js";
import type { DataInfoT, AccountPermission, SearchResult} from "./protocalT.js";

export class ServerConn {
    async authUsr( encKey: string ): Promise<AccountPermission>{

            const params = new URLSearchParams();
            params.set("key", encKey);
            params.set("require_permission", "true");

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
    
    async reqFileList( tags: string[] ): Promise<DataInfoT[]>{
        const concatTags = tags.join("&&");
        const url = new URL(`${getBackendURL()}/filelist`);
        url.searchParams.append("tags", concatTags);

        const response = await fetch(url.toString());
        if (response.ok){
            const resObj = await response.json();
            const DataInfoList: DataInfoT[] = resObj.data;
            return DataInfoList;
        }
        else {
            throw new Error(`Got response: ${response.status}`)
        }
    };

    async reqDatapointSummary( uid: string ): Promise<DataInfoT>{
        const url = new URL(`${getBackendURL()}/fileinfo/${uid}`);
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

    async reqDatapointAbstract(uid: string): Promise<string>{
        const params = new URLSearchParams();
        params.set("key", getCookie("encKey"));
        const response = await fetch(`${getBackendURL()}/fileinfo-supp/abstract/${uid}`);
        if (response.ok && response.status === 200) {
            const res: string = await response.text();
            return res
        }
        else{
            throw new Error(`Got response: ${response.status}`);
        }
    }


    async reqDatapointNote( uid: string ): Promise<string>{
        const url = new URL(`${getBackendURL()}/fileinfo-supp/note/${uid}`);
        url.searchParams.append("key", getCookie("encKey"));
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
        url.searchParams.append("key", getCookie("encKey"));
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

    /* upload images to the misc folder and return the file names */
    async uploadImages(uid: string, files: File[]): Promise<string[]>{
        const res = await Promise.all(
            files.map((file) => {
                // file is an object of File class: https://developer.mozilla.org/en-US/docs/Web/API/File
                return new Promise((resolve, reject) => {
                    const form = new FormData();
                    form.append('file', file);
                    
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

    async editData(uid: string | null, bibtex: string, tags: string[] = [], url: string = ""): Promise<DataInfoT>{
        const params = new URLSearchParams();
        if (!uid){ uid = null; }
        params.set("key", getCookie("encKey"));
        params.set("uuid", JSON.stringify(uid))
        params.set("bibtex", bibtex);
        params.set("tags", JSON.stringify(tags));
        params.set("url", url);
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

    async search(method: string, kwargs: any): Promise<SearchResult>{
        const params = new URLSearchParams();

        params.set("key", getCookie("encKey"));
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

    async addArxivPaperByID( id: string,): Promise<DataInfoT>{
        if (!id.startsWith("arxiv:")){
            id = "arxiv:" + id;
        }
        const params = new URLSearchParams();
        params.set("key", getCookie("encKey"));
        params.set("retrive", id);
        params.set("tags", JSON.stringify(["arxiv_feed"]))

        const response = await fetch(`${getBackendURL()}/collect?${params.toString()}`, 
            {
                method: "POST",
                headers: {
                    "Content-Type":"application/x-www-form-urlencoded"
                },
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

    async featurize(text: string): Promise<number[]>{
        const params = new URLSearchParams();
        params.set("key", getCookie("encKey"));
        params.set("text", text);

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

    // ============== Manipulate data ==============
    async deleteData(uid: string): Promise<boolean>{
        const url = new URL(`${getBackendURL()}/dataman/delete`);
        url.searchParams.append("key", getCookie("encKey"));
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
}
