
import { ServerConn } from "@/core/serverConn";
import { STAY_LOGIN_DAYS } from "@/config";
import { setCookie, getCookie } from "../libs/cookie";
import type { AccountPermission } from "@/core/protocalT";

export function saveAuthentication(
    encKey: string, 
    permission: AccountPermission, 
    stayLogin: boolean,
    keepDays: number|null = STAY_LOGIN_DAYS,
    ){
        setCookie("encKey", encKey, keepDays);
        setCookie("accountPermission", JSON.stringify(permission), keepDays);
        setCookie("keepLogin", stayLogin?"1":"0", keepDays);
    }

// Use cookie to authenticate again and refresh stay-login time
export async function cookieAuthentication(keepDays: number = STAY_LOGIN_DAYS): Promise<AccountPermission> {
    const conn = new ServerConn();
    const usrEncKey = getCookie("usrEncKey");
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