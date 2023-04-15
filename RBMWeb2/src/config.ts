
// export const DOMAINURL = "http://" + window.location.hostname;
// export const PORT = window.location.port;

let DOMAINURL: string, PORT: string;
let BACKENDURL: string, FRONTENDURL: string;
if (import.meta.env.DEV){
    DOMAINURL = "http://limengxun.com";
    PORT = "8080";
    BACKENDURL = `${DOMAINURL}:${PORT}`;
    FRONTENDURL = `http://${window.location.hostname}:${window.location.port}`; //
}
else{
    // production code
    DOMAINURL = "http://" + window.location.hostname;
    PORT = window.location.port;
    BACKENDURL = `${DOMAINURL}:${PORT}`;
    FRONTENDURL = `${DOMAINURL}:${PORT}/frontend`; //
}
export {DOMAINURL, PORT, BACKENDURL, FRONTENDURL};
export const STAY_LOGIN_DAYS: number = 3;

export const LOCATIONS = {
    "main": FRONTENDURL,
    "login": `${FRONTENDURL}/login.html`
}
