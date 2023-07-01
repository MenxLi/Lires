
import { getCookie } from "./libs/cookie";

export function platformType(){
    if ((window as any).__TAURI__){
        return "tauri";
    }
    else{
        return "web";
    }
}

// get protocal from the current page
let FRONTEND_PROTOCAL: 'http:' | 'https:' = window.location.protocol as 'http:' | 'https:';

let FRONTENDURL: string;
FRONTENDURL = `${FRONTEND_PROTOCAL}//${window.location.hostname}:${window.location.port}`; //
if (import.meta.env.DEV){
    console.log("DEV mode");
}
else{
    // production code
    console.log("production mode")
}
function getBackendURL(){
    let BACKEND_PROTOCAL: 'http:' | 'https:' = window.location.protocol as 'http:' | 'https:';
    let BACKEND_PORT = "8080"
    let HOSTNAME = window.location.hostname;
    let BACKENDURL: string;
    if (getCookie("backendPort")){
        BACKEND_PORT = getCookie("backendPort");
    }
    if (platformType() === "tauri"){
        // BACKEND_PROTOCAL = "https:";     // assume the backend is https
        // HOSTNAME = "limengxun.com";
        console.log("tauri mode!")
    }
    BACKENDURL = `${BACKEND_PROTOCAL}//${HOSTNAME}:${BACKEND_PORT}`;
    return BACKENDURL;
}

export {getBackendURL, FRONTENDURL};
export const STAY_LOGIN_DAYS: number = 3;
export const MAINTAINER = {
    name: "Li, Mengxun",
    email: "mengxunli@whu.edu.cn"
}
