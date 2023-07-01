
import { getCookie } from "./libs/cookie";

export function platformType(){
    if ((window as any).__TAURI__){
        return "tauri";
    }
    else{
        return "web";
    }
}

let DOMAINURL: string, PORT: string;
let FRONTENDURL: string;
if (import.meta.env.DEV){
    DOMAINURL = `http://${window.location.hostname}`
    PORT = "8080";
    FRONTENDURL = `http://${window.location.hostname}:${window.location.port}`; //
}
else{
    // production code
    DOMAINURL = "http://" + window.location.hostname;
    PORT = window.location.port;
    FRONTENDURL = `${DOMAINURL}:${PORT}`; //
}
function getBackendURL(){
    let BACKEND_PORT = "8080"
    let BACKENDURL: string;
    if (getCookie("backendPort")){
        BACKEND_PORT = getCookie("backendPort");
    }
    if (platformType() !== "tauri"){
        BACKENDURL = `${DOMAINURL}:${BACKEND_PORT}`;
    }
    else{
        // Tauri app
        // Will be changed to the real backend URL in the future
        BACKENDURL = `http://limengxun.com:${BACKEND_PORT}`;
    }
    return BACKENDURL;
}
export {getBackendURL, FRONTENDURL};
export const STAY_LOGIN_DAYS: number = 3;

export const MAINTAINER = {
    name: "Li, Mengxun",
    email: "mengxunli@whu.edu.cn"
}
