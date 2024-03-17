

/*
 * expDays: set to null for session cookie
* */
function setCookie(key: string, value: string, expDays: number|null = null): void{
    let expStr = "";
    if (expDays){
        let date = new Date();
        date.setTime(date.getTime() + (expDays * 24 * 60 * 60 * 1000));
        expStr = `expires=${date.toUTCString()}; `
    }
    document.cookie = `${key}=${value}; ${expStr} path=/; sameSite=Lax`
}

// check if the cookie is kept with expiration date
function isCookieKept(key: string): boolean {
    const cookie_decode = decodeURIComponent(document.cookie);
    const split_cookie = cookie_decode.split("; ");
    split_cookie.forEach((val) => {
        if (val.startsWith(`${key}=`) && val.includes(`expires`)){
            return true;
        }
    })
    return false;
}


function getCookie(key: string): string {
    const cookie_decode = decodeURIComponent(document.cookie);
    const split_cookie = cookie_decode.split("; ");
    let ret = "";
    split_cookie.forEach((val) => {
        if (val.indexOf(key) === 0){
            ret = val.substring(`${key}=`.length);
        }
    })
    return ret;
}

export {setCookie, getCookie, isCookieKept};
