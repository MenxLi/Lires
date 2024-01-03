import type { DataPoint } from "./dataClass";
import { getBackendURL } from "../config";
import { URLRouter } from "./vueInterface";
import type { Router } from "vue-router";

// parse raw markdown to mardown with proper html links
export function parseMarkdown(content: string, {
    router = null as null | Router,
    datapoint = null as null | DataPoint,
}) : string{

    // url router is used for updating url with query params
    const urlRouter = router? new URLRouter(router): null;

    if (datapoint) {
        // replace relative file links to absolute web links
        content = content.replace(new RegExp('./misc/', 'g'), `${getBackendURL()}/img/${datapoint!.summary.uuid}\\?fname=`);

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