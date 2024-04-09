import type { DataPoint } from "./dataClass";
import { getBackendURL } from "../config";
import { URLRouter } from "./vueInterface";
import { useDataStore } from "../components/store";
import type { Router } from "vue-router";

export interface FrontMatterData {
    links?: Record<string, string>;
}

// parse raw markdown to mardown with proper html links
export function parseMarkdown(content: string, {
    router = null as null | Router,
    datapoint = null as null | DataPoint,
}) : string{

    // url router is used for updating url with query params
    const urlRouter = router? new URLRouter(router): null;

    // remove gray-matter front matter
    content = content.replace(/^---[\s\S]*?---/, '');

    if (datapoint) {
        // need to know the user in order to identify which database to use
        const user = useDataStore().user

        // replace relative file links to absolute web links
        content = content.replace(
            new RegExp('./misc/', 'g'), 
            `${getBackendURL()}/misc/${datapoint!.summary.uuid}?_u=${user.id}&&fname=`
            );

        if (urlRouter) {
            // replace ${doc}#.Router (current page with ?docHashMark=...) if in reader, else (dataurl page with #...)
            const currentURL = window.location.href;
            if(currentURL.includes('/reader/')){
                content = content.replace(new RegExp('\\$\\{doc\\}#', 'g'), urlRouter.updateURLWithParam('docHashMark', ''));
            }
            else{
                content = content.replace(new RegExp('\\$\\{doc\\}#', 'g'), `${datapoint!.getOpenDocURL()}#`);
            }
        }
    }

    return content;
}