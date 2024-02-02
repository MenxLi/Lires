
import { ServerConn } from "./serverConn";
import { useSettingsStore, useDataStore } from "../components/store";
import type { UserInfo } from "./protocalT";
import { sha256 } from "../utils/sha256lib";

export function saveAuthentication(
    encKey: string, 
    userInfo: UserInfo|null, 
    stayLogin: boolean,
    ){
        useSettingsStore().setEncKey(encKey, stayLogin);

        if (userInfo !== null) useDataStore().user = userInfo;
        else useDataStore().clearUserInfo() 

        if (userInfo) useSettingsStore().loggedIn = true;
        else // null indicates logout
            useSettingsStore().loggedIn = false;
    }

// Check if logged out using cookies, no server authentication
export function checkSettingsLogout(){
    return !Boolean(useSettingsStore().encKey);
}

// completely remove the encKey, and set loggedIn to false
export function settingsLogout(){
    saveAuthentication("", null, true);
}

// Use current settings to authenticate again
// Will be called when the page is loaded or on navigation
export async function settingsAuthentication(): Promise<UserInfo|null> {
    const conn = new ServerConn();
    const usrEncKey = useSettingsStore().encKey;
    try{
        const userInfo = await conn.authUsr(usrEncKey);
        saveAuthentication( usrEncKey, userInfo, true);
        return userInfo;
    } catch (e){
        console.log("settingsAuthentication failed: ", e);
        // settingsLogout();
        return null;
    }
}

export function getEncKey(username: string, password: string){
    return sha256(username + sha256(password));
}