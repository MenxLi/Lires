
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
        if (!import.meta.env.DEV){
            // assume the backend is https in tauri production mode, 
            // because we've used broswer fetch api for api requests
            // however tauri use native webview, which can not access http backend
            // the backend should be deployed on the server with ssl certificate
            BACKEND_PROTOCAL = "https:";     
            // set fixed host, may be changed in the future
            HOSTNAME = "limengxun.com";
        }
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
