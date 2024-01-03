import type { DataPoint } from "./dataClass";
import { getBackendURL } from "../config";

// parse raw markdown to mardown with proper html links
export function parseMarkdown(content: string, context = {
    datapoint : null as null | DataPoint,
}) : string{
    if (context.datapoint) {
        // replace relative file links to absolute web links
        content = content.replace(new RegExp('./misc/', 'g'), `${getBackendURL()}/img/${context.datapoint!.summary.uuid}\\?fname=`);
    }

    return content;
}