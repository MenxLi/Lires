
import { getBackendURL } from "../config";
import { useSettingsStore } from "../components/store";
import { sha256 } from "../libs/sha256lib";

export class ServerWebsocketConn{
    declare ws: WebSocket
    declare sessionID: string

    constructor(){
        this.sessionID = sha256(Date.now().toString()).slice(0, 16);
        this.init()
    }

    get settings(){
        return useSettingsStore();
    }

    private init(){
        const urlParams = new URLSearchParams(window.location.search);
        urlParams.append('key', this.settings.encKey);
        urlParams.append('session_id', this.sessionID);
        const __ws_backend = getBackendURL().replace('https://', 'wss://').replace('http://', 'ws://')
            + '/ws?' + urlParams.toString();
        
        console.log("connecting to server websocket at: ", __ws_backend);

        this.ws = new WebSocket(__ws_backend);

        this.ws.onmessage = (event) => {
            // TODO: handle message with hooks
            console.log(event)
        }
        this.ws.onopen = () => {
            console.log("connected to server websocket");
        }
        this.ws.onclose = () => {
            console.log("server websocket closed, will try to reconnect in 10 second");
            new Promise(r => setTimeout(r, 10000)).then(
                () => {
                    if (this.ws.readyState === WebSocket.CLOSED) this.init()
                }
            )
        }
    }

    public send(data: any){
        if (this.ws.readyState === WebSocket.OPEN){
            this.ws.send(JSON.stringify(data));
        }
        else{
            console.log("server websocket not ready, cannot send data");
        }
    }

    public close(){
        if (this.ws.readyState === WebSocket.OPEN){
            this.ws.close();
        }
        else{
            console.log("server websocket not ready, cannot close");
        }
    }
}