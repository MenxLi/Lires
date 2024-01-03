import type { DataPoint } from "./dataClass";
import { getBackendURL } from "../config";

function assert(condition: any, msg?: string): asserts condition {
    if (!condition) {
        throw new Error("Assertion failed: " + msg);
    }
}

// parse raw markdown to mardown with proper html links
export function parseMarkdown(content: string, context = {
    datapoint : null as null | DataPoint,
}) : string{
    if (context.datapoint) {
        // replace relative file links to absolute web links
        content = content.replace(new RegExp('./misc/', 'g'), `${getBackendURL()}/img/${context.datapoint!.summary.uuid}\\?fname=`);

        // replace ${doc}#... to (current page with ?docHashMark=...) if in reader, else (dataurl page with #...)
        const currentURL = window.location.href;
        if(currentURL.includes('/reader/')){
            content = content.replace(new RegExp('\\$\\{doc\\}#', 'g'), `${currentURL}?docHashMark=`);
        }
        else{
            content = content.replace(new RegExp('\\$\\{doc\\}#', 'g'), `${context.datapoint!.getOpenDocURL()}#`);
        }
    }

    return content;
}