
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
}
