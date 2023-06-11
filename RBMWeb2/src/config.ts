
// export const DOMAINURL = "http://" + window.location.hostname;
// export const PORT = window.location.port;
import { getCookie } from "./libs/cookie";

let DOMAINURL: string, PORT: string;
let FRONTENDURL: string;
if (import.meta.env.DEV){
    // DOMAINURL = "http://limengxun.com";
    DOMAINURL = "http://127.0.0.1";
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
    if (getCookie("backendPort")){
        BACKEND_PORT = getCookie("backendPort");
    }
    const BACKENDURL = `${DOMAINURL}:${BACKEND_PORT}`;
    return BACKENDURL;
}
export {getBackendURL, FRONTENDURL};
export const STAY_LOGIN_DAYS: number = 3;

export const LOCATIONS = {
    "main": FRONTENDURL,
    "login": `${FRONTENDURL}/login.html`
}

export const MAINTAINER = {
    name: "Li, Mengxun",
    email: "mengxunli@whu.edu.cn"
}
