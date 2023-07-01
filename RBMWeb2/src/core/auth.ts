
import { ServerConn } from "./serverConn";
import { useSettingsStore } from "../components/store";
import type { AccountPermission } from "./protocalT";

export function saveAuthentication(
    encKey: string, 
    permission: AccountPermission|null, 
    stayLogin: boolean,
    ){
        useSettingsStore().setEncKey(encKey, stayLogin);
        if (permission){ useSettingsStore().accountPermission = permission; }
    }

// Check if logged out using cookies, no server authentication
export function checkSettingsLogout(){
    return !Boolean(useSettingsStore().encKey);
}

export function settingsLogout(){
    saveAuthentication("", null, true);
}

// Use cookie to authenticate again and refresh stay-login time
export async function settingsAuthentication(): Promise<AccountPermission> {
    const conn = new ServerConn();
    const usrEncKey = useSettingsStore().encKey;
    const permission = conn.authUsr(usrEncKey);
    permission.then(
        (accountPermission) => {
            saveAuthentication(
                usrEncKey, accountPermission, false,
            );
        }
    )
    return permission;
}