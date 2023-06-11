
import { ServerConn } from "./serverConn";
import { STAY_LOGIN_DAYS } from "../config";
import { setCookie, getCookie } from "../libs/cookie";
import type { AccountPermission } from "./protocalT";

export function saveAuthentication(
    encKey: string, 
    permission: AccountPermission|null, 
    stayLogin: boolean,
    keepDays: number|null = STAY_LOGIN_DAYS,
    ){
        setCookie("encKey", encKey, keepDays);
        if (permission){ setCookie("accountPermission", JSON.stringify(permission), keepDays); }
        else{ setCookie("accountPermission", "", 0)}
        setCookie("keepLogin", stayLogin?"1":"0", keepDays);
    }

// Check if logged out using cookies, no server authentication
export function checkCookieLogout(){
    return !Boolean(getCookie("encKey"));
}

export function cookieLogout(){
    saveAuthentication("", null, false, 0);
}

// Use cookie to authenticate again and refresh stay-login time
export async function cookieAuthentication(keepDays: number = STAY_LOGIN_DAYS): Promise<AccountPermission> {
    const conn = new ServerConn();
    const usrEncKey = getCookie("encKey");
    const stayLogin: boolean = Number.parseInt(getCookie("keepLogin")) == 1? true:false;
    let _keepTime: null |number = null;
    if (stayLogin){
        _keepTime = keepDays;
    }
    const permission = conn.authUsr(usrEncKey);
    permission.then(
        (accountPermission) => {
            saveAuthentication(
                usrEncKey, accountPermission, stayLogin, _keepTime
            );
        }
    )
    return permission;
}