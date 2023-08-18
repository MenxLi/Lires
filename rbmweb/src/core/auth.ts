
import { ServerConn } from "./serverConn";
import { useSettingsStore } from "../components/store";
import type { AccountPermission } from "./protocalT";

export function saveAuthentication(
    encKey: string, 
    permission: AccountPermission|null, 
    stayLogin: boolean | null,
    ){
        useSettingsStore().setEncKey(encKey, stayLogin);
        useSettingsStore().accountPermission = permission;
        if (permission){
            useSettingsStore().loggedIn = true;
        }
        else{
            // null indicates logout
            useSettingsStore().loggedIn = false;
        }
    }

// Check if logged out using cookies, no server authentication
export function checkSettingsLogout(){
    return !Boolean(useSettingsStore().encKey);
}

export function settingsLogout(){
    saveAuthentication("", null, true);
}

// Use current settings to authenticate again
// Will be called when the page is loaded or on navigation
export async function settingsAuthentication(): Promise<AccountPermission|null> {
    const conn = new ServerConn();
    const usrEncKey = useSettingsStore().encKey;
    try{
        const permission = await conn.authUsr(usrEncKey);
        saveAuthentication( usrEncKey, permission, null);
        return permission;
    } catch (e){
        console.log("settingsAuthentication failed: ", e);
        saveAuthentication("", null, true);
        return null;
    }
}