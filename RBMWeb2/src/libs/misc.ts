
// not used for now, a backup for the future
export function resolveAbsoluteURL(url: string){
    const baseUrl = new URL(import.meta.url);
    baseUrl.pathname = baseUrl.pathname.replace(/\/[^/]*$/, '/');
    return new URL(url, baseUrl).href;
}