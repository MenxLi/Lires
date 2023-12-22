
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
    eventType: Event['type'] | Event['type'][], 
    eventReactFn: (arg: Event)=>void)
    {
    if (Array.isArray(eventType)){
        for (const et of eventType){
            registerServerEvenCallback(et, eventReactFn);
        }
        return;
    }
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
    declare __eventCallback_records: {
        onopenCallback: ()=>void,
        onmessageCallback: (arg: MessageEvent)=>void,
        oncloseCallback: ()=>void
    }

    constructor(){
        this.sessionID = sha256(Date.now().toString()).slice(0, 16);
        this.__eventCallback_records = {
            onopenCallback: ()=>{},
            onmessageCallback: (_)=>{},
            oncloseCallback: ()=>{}
        }
    }

    get settings(){
        return useSettingsStore();
    }

    public isOpen=()=>(this.ws)?(this.ws.readyState === WebSocket.OPEN):false;

    public init({
        onopenCallback = ()=>{},
        onmessageCallback = (_: MessageEvent)=>{},
        oncloseCallback = ()=>{}
    } = {}
    ): ServerWebsocketConn{
        // keep a record of the callback functions, so that we can re-init the websocket connection
        this.__eventCallback_records = {
            onopenCallback,
            onmessageCallback,
            oncloseCallback
        }

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
            onmessageCallback(msg);
        }
        this.ws.onopen = () => {
            console.log("connected to server websocket");
            onopenCallback();
        }
        this.ws.onclose = () => {
            console.log("server websocket closed, will try to reconnect in 10 second");
            oncloseCallback();
            new Promise(r => setTimeout(r, 10000)).then(
                () => {
                    if (this.ws.readyState === WebSocket.CLOSED) this.init({
                        onopenCallback,
                        onmessageCallback,
                        oncloseCallback
                    })
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

    // reset the websocket connection using cached callback functions
    public reset(){
        if (this.ws.readyState === WebSocket.OPEN){
            this.ws.close();
        }
        this.init(this.__eventCallback_records);
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