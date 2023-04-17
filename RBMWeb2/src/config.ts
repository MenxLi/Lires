
// export const DOMAINURL = "http://" + window.location.hostname;
// export const PORT = window.location.port;
import { getCookie } from "./libs/cookie";

let DOMAINURL: string, PORT: string;
let BACKENDURL: string, FRONTENDURL: string;
if (import.meta.env.DEV){
    DOMAINURL = "http://limengxun.com";
    PORT = "8080";
    FRONTENDURL = `http://${window.location.hostname}:${window.location.port}`; //
}
else{
    // production code
    DOMAINURL = "http://" + window.location.hostname;
    PORT = window.location.port;
    FRONTENDURL = `${DOMAINURL}:${PORT}/frontend`; //
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
