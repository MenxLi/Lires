
// import { getCookie } from "./libs/cookie";
import { useSettingsStore } from "./components/store";

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
    const BACKEND_PORT = useSettingsStore().backendPort;
    const BACKEND_HOST = useSettingsStore().backendUrl;
    return `${BACKEND_HOST}:${BACKEND_PORT}`;
}

export {getBackendURL, FRONTENDURL};
export const MAINTAINER = {
    name: "Li, Mengxun",
    email: "mengxunli@whu.edu.cn"
}
