
import { getBackendURL } from "../config";
import { useSettingsStore } from "../components/store";
import { sha256 } from "../libs/sha256lib";
import type { Event } from "./protocalT";

// Declare the global object
declare global {
    interface Window {
        g_eventHooks: Record<string, ((arg: Event)=>void)[]>;
        g_wsConn: ServerWebsocketConn;
    }
  }
const __global_eventHooks: Record<string, ((arg: Event)=>void)[]> = {};
window.g_eventHooks = __global_eventHooks

/*
    Register a hook function to a specific event type, 
    the server will send the event to the client, and the client will react to that kind of event
 */
export function registerServerEvenCallback( 
    eventType: Event['type'], 
    eventReactFn: (arg: Event)=>void)
    {
    if (__global_eventHooks[eventType] === undefined){
        __global_eventHooks[eventType] = [];
    }
    __global_eventHooks[eventType].push(eventReactFn);
}

export function getSessionConnection(): ServerWebsocketConn{
    if (window.g_wsConn === undefined){
        window.g_wsConn = new ServerWebsocketConn()
    }
    return window.g_wsConn
}


export class ServerWebsocketConn{
    declare ws: WebSocket
    declare sessionID: string

    constructor(){
        this.sessionID = sha256(Date.now().toString()).slice(0, 16);
    }

    get settings(){
        return useSettingsStore();
    }

    public init(): ServerWebsocketConn{
        const urlParams = new URLSearchParams(window.location.search);
        urlParams.append('key', this.settings.encKey);
        urlParams.append('session_id', this.sessionID);
        const __ws_backend = getBackendURL().replace('https://', 'wss://').replace('http://', 'ws://')
            + '/ws?' + urlParams.toString();
        
        console.log("connecting to server websocket at: ", __ws_backend);

        this.ws = new WebSocket(__ws_backend);

        this.ws.onmessage = (msg) => {
            // TODO: handle message with hooks
            console.log(msg)
            const data = JSON.parse(msg.data);
            if (data['type'] === 'event'){
                const serverEvent: Event = data.content;
                console.log(serverEvent)
                if (Object.keys(__global_eventHooks).includes(serverEvent.type)){
                    for (const hook_fn of __global_eventHooks[serverEvent.type]){
                        hook_fn(serverEvent);
                    }
                }
            }
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

        return this;
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