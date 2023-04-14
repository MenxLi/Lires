
// Server connection

import {BACKENDURL} from "../config.js";
import type { DataInfoT } from "./protocalT.js";

export class ServerConn {
     authUsr(
        encKey: string,
        {
            onSuccess = function(){},
            onFailure = function(msg){},
        }: {
            onSuccess?: ()=>void;
            onFailure?: (msg: string)=>void;
        } = {}): void{

            const params = new URLSearchParams();
            params.set("key", encKey);

            fetch(`${BACKENDURL}/auth`, 
                  {
                      method: "POST",
                      headers: {
                          "Content-Type":"application/x-www-form-urlencoded"
                      },
                      body: params.toString()
                  }).then(
                      (response) => {
                          if (response.ok){
                              return response.text();
                          }
                          else{
                              return `Failed - ${response.status.toString()}`;
                          }
                      }
                  ).then(
                      (data) => {
                          if (data == "Success"){
                              onSuccess();
                          }
                          else{
                              onFailure(data);
                          }
                      }
                  )
    }

    
    async reqFileList( tags: string[] ): Promise<DataInfoT[]>{
        const concatTags = tags.join("&&");
        const url = new URL(`${BACKENDURL}/filelist`);
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
