
// not used for now, a backup for the future
export function resolveAbsoluteURL(url: string){
    const baseUrl = new URL(import.meta.url);
    baseUrl.pathname = baseUrl.pathname.replace(/\/[^/]*$/, '/');
    return new URL(url, baseUrl).href;
}

export function formatAuthorName(author: string): string{
    // the author name may be in the form of 
    // <Family Name>, <Given Name> <...>
    // <Given Name> <...> <Family Name> 
    // make sure formatted author is named as <Family Name>, <Given Name> in lower case

    author = author.trim().toLowerCase();

    let formattedAuthor = author.trim(); // Remove leading/trailing whitespace
    // Check if the author name contains a comma
    if (formattedAuthor.includes(',')) {
        const [familyName, givenName] = formattedAuthor.split(',', 2);
        formattedAuthor = `${familyName.trim()}, ${givenName.trim()}`;
    } else {
        // check if no space in the author name
        if (formattedAuthor.indexOf(' ') === -1){
            return formattedAuthor;
        }

        // If there is no comma, assume the last space separates the family name and given name
        const lastIndex = formattedAuthor.lastIndexOf(' ');
        const familyName = formattedAuthor.slice(lastIndex + 1);
        const givenName = formattedAuthor.slice(0, lastIndex);
        formattedAuthor = `${familyName.trim()}, ${givenName.trim()}`;
    }

    return formattedAuthor;
}

/* detect if an element is visible in the viewport */
export function isVisiable(el: HTMLElement): boolean{
    if (!el){
        // console.log("no element");
        return false;
    }
    if (el.style.display === "none"){
        // console.log("display none");
        return false;
    }
    if (el.style.visibility === "hidden"){
        // console.log("visibility hidden");
        return false;
    }
    if (el.style.opacity === "0"){
        // console.log("opacity 0");
        return false;
    }

    const rect = el.getBoundingClientRect();
    // console.log(rect.top, rect.bottom, window.innerHeight)
    if (rect.top < 0){
        return false;
    }
    if (rect.bottom > window.innerHeight){
        return false;
    }
    return true;
}