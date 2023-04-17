
// Server connection

import {getBackendURL} from "../config.js";
import type { DataInfoT, AccountPermission } from "./protocalT.js";

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
}
