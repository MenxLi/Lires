
import { sha256 } from "../utils/sha256lib";
import type { Event } from "./protocol";
import { onMounted, onUnmounted } from "vue";

// Declare the global object
declare global {
    interface Window {
        g_eventHooks: Record<string, ((arg: Event)=>void)[]>;
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
    if (!__global_eventHooks[eventType].includes(eventReactFn)){
        __global_eventHooks[eventType].push(eventReactFn);
    }
}

export function unregisterServerEvenCallback(
    eventType: Event['type'] | Event['type'][], 
    eventReactFn: (arg: Event)=>void)
    {
    if (Array.isArray(eventType)){
        for (const et of eventType){
            unregisterServerEvenCallback(et, eventReactFn);
        }
        return;
    }
    if (__global_eventHooks[eventType] === undefined){
        return;
    }
    __global_eventHooks[eventType] = __global_eventHooks[eventType].filter(
        (fn)=>fn !== eventReactFn
    );
}

/* 
    This function will automatically register and unregister the event callback 
    when the component is mounted and unmounted
 */
export function registerServerEvenCallback_auto(
    eventType: Event['type'] | Event['type'][], 
    eventReactFn: (arg: Event)=>void){

    onMounted(()=>{
        registerServerEvenCallback(eventType, eventReactFn);
        console.log(`registered event callback [${eventType}]`, eventReactFn.name);
    });
    onUnmounted(()=>{
        unregisterServerEvenCallback(eventType, eventReactFn);
        console.log(`unregistered event callback [${eventType}]`, eventReactFn.name);
    });
}

export class ServerWebsocketConn{
    declare ws: WebSocket
    declare sessionID: string
    declare __baseUrlGetter: ()=>string
    declare __tokenGetter: ()=>string
    declare __remainingRetries: number
    declare __eventCallback_records: {
        onopenCallback: ()=>void,
        onmessageCallback: (arg: MessageEvent)=>void,
        oncloseCallback: ()=>void
        onfailedToConnectCallback: ()=>void
    }

    constructor( baseUrlGetter: ()=>string, tokenGetter: ()=>string){
        this.__baseUrlGetter = baseUrlGetter;
        this.__tokenGetter = tokenGetter;
        this.resetRemainingRetries();
        this.sessionID = sha256(Date.now().toString()).slice(0, 16);
        this.__eventCallback_records = {
            onopenCallback: ()=>{},
            onmessageCallback: (_)=>{},
            oncloseCallback: ()=>{},
            onfailedToConnectCallback: ()=>{}
        }
    }

    private resetRemainingRetries=()=>{this.__remainingRetries = 10;}
    private decreaseRemainingRetries=()=>{this.__remainingRetries -= 1;}
    public isOpen=()=>(this.ws)?(this.ws.readyState === WebSocket.OPEN):false;
    public willTryReconnect=()=>this.__remainingRetries > 0;

    public connect({
        onopenCallback = ()=>{},
        onmessageCallback = (_: MessageEvent)=>{},
        oncloseCallback = ()=>{},
        onfailedToConnectCallback = ()=>{}
    } = {}
    ): ServerWebsocketConn{
        // keep a record of the callback functions, so that we can re-init the websocket connection
        this.__eventCallback_records = {
            onopenCallback,
            onmessageCallback,
            oncloseCallback,
            onfailedToConnectCallback,
        }

        const urlParams = new URLSearchParams(window.location.search);
        urlParams.append('key', this.__tokenGetter());
        urlParams.append('session_id', this.sessionID);
        const __ws_backend = this.__baseUrlGetter().replace('https://', 'wss://').replace('http://', 'ws://')
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
            this.resetRemainingRetries()
        }
        this.ws.onclose = () => {
            console.log("server websocket closed, will try to reconnect in 1 second");
            oncloseCallback();
            if (this.willTryReconnect()){
                this.decreaseRemainingRetries();
                new Promise(r => setTimeout(r, 1000)).then(
                    () => {
                        if (this.ws.readyState === WebSocket.CLOSED) this.connect({
                            onopenCallback,
                            onmessageCallback,
                            oncloseCallback,
                            onfailedToConnectCallback,
                        })
                    });
            }else{
                onfailedToConnectCallback();
            }
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
    public resetReconnect(){
        if (this.ws && this.ws.readyState === WebSocket.OPEN){
            this.ws.close();
        }
        this.resetRemainingRetries()
        this.connect(this.__eventCallback_records);
    }

    public close(){
        if (this.ws && this.ws.readyState === WebSocket.OPEN){
            this.__remainingRetries = 0;    // disable reconnect
            this.ws.close();
        }
        else{
            console.log("server websocket not ready, cannot close");
        }
    }
}