
import { defineStore } from 'pinia'
import { DataBase } from '../core/dataClass'
import { UserPool } from '../core/user'
import { DataTags } from '../core/tag'
import { ServerConn } from '../api/serverConn'
import { ServerWebsocketConn } from '../api/serverWebsocketConn'
import { formatAuthorName } from '../utils/misc'
import { setCookie, getCookie, isCookieKept } from '../utils/cookie'
export { formatAuthorName }
import type { SearchStatus, PopupStyle, TagStatus } from './interface'
import type { UserInfo } from '../api/protocol'

interface PopupValue {
    content: string,
    styleType: PopupStyle,
}


export const useUIStateStore = defineStore(
    "uiStatus", {
        state: () => {
            return {
                // home component
                tagStatus: {
                    checked: new DataTags(),
                    all: new DataTags(),
                    unfolded: new DataTags(),
                } as TagStatus,

                shownDataUIDs: [] as string[],
                shownDataScores: [] as number[] | null,
                searchState: {
                        "searchBy": "title",
                        "content": ""
                    } as SearchStatus,
                unfoldedDataUIDs: [] as string[],

                // reader component
                recentlyReadDataUIDs: [] as string[],
                preferredReaderLeftPanelWidthPerc: 0.65,
                showMiscPanel: false,
                showNotePreview: null as boolean | null,

                // global popup component, need to be initialized in App.vue
                popupValues : {} as Record<string, PopupValue>,

                // global database loading status
                databaseLoadingStatus: {
                    nCurrent: 0,
                    nTotal: -1,
                },

                // global data editor status
                dataEditorOpened: false,
            }
        },
        getters: {
            databaseLoadingProgress(): number {
                if (this.databaseLoadingStatus.nTotal === -1){
                    if (this.databaseLoadingStatus.nCurrent === 0) return 0.0;
                    else return 1.0;
                }
                else{
                    return this.databaseLoadingStatus.nCurrent / this.databaseLoadingStatus.nTotal;
                }

            }, 
            
            focusedDataUID(): string | null {
                if (this.unfoldedDataUIDs.length === 0){
                    return null;
                }
                return this.unfoldedDataUIDs[0];
            }

        },
        actions: {
            updateShownData(){
                // update shownDataUIDs, which is used to control the display of data cards
                // Should call this function manually, because it involves async operation (searching)
                const dataStore = useDataStore();
                this.tagStatus.all = dataStore.allTags;     // in case tag pool are updated from the backend
                console.log("DEBUG: updateShownData() is called.")
                useConnectionStore().conn.query(
                    {
                        tags: Array.from(this.tagStatus.checked),
                        searchBy: this.searchState.searchBy,
                        searchContent: this.searchState.content,
                    }
                ).then(
                    (res) => {
                        this.shownDataUIDs = res.uids;
                        this.shownDataScores = res.scores;
                    }
                )
            },
            addRecentlyReadDataUID(uid: string){
                if (this.recentlyReadDataUIDs.includes(uid)){
                    this.recentlyReadDataUIDs.splice(this.recentlyReadDataUIDs.indexOf(uid), 1);
                }
                this.recentlyReadDataUIDs.unshift(uid);
                if (this.recentlyReadDataUIDs.length > 5){
                    this.recentlyReadDataUIDs.pop();
                }
            },
            showPopup(
                content: string, 
                style: PopupStyle = "info",
                time: number = 3000     // in ms
                ){
                const id = Math.random().toString();
                this.popupValues[id] = {
                    content: content,
                    styleType: style,
                };
                setTimeout(() => {
                    delete this.popupValues[id];
                }, time);
            },
            reloadDatabase(){
                useDataStore().reload(
                    () => {
                        this.databaseLoadingStatus.nCurrent = 0; // databaseLoadingStatus get unused for now
                        useDataStore().database.clear();
                        this.updateShownData()
                    },
                    () => {
                        useUIStateStore().databaseLoadingStatus.nTotal = -1
                        useUIStateStore().tagStatus.all = useDataStore().database.allTags();
                        this.updateShownData(); 
                    },
                    () => {
                        this.showPopup(`Failed to load database from: ${useConnectionStore().conn.baseURL}`, "alert");
                        useUIStateStore().databaseLoadingStatus.nTotal = -1
                    },
                )

            }
        }
    }
)

export const useConnectionStore = defineStore(
    "connection", {
        state: () => {
            const wsConn = new ServerWebsocketConn(
                useSettingsStore().backend,
                () => useSettingsStore().encKey
            )
            const conn = new ServerConn(
                    useSettingsStore().backend,
                    () => useSettingsStore().encKey,
                    () => wsConn.sessionID,
                )
            return { conn, wsConn }
        },
    }
)

export const useDataStore = defineStore(
    "data", {
        state: () => {
            return {
                // @ts-ignore
                database: new DataBase(useConnectionStore().conn),
                // @ts-ignore
                userPool: new UserPool(useConnectionStore().conn),
                user: {
                    id: -1,
                    username: '',
                    enc_key: '',
                    name: '',
                    is_admin: false,
                    mandatory_tags: [],
                    has_avatar: false,
                    max_storage: 0,
                } as UserInfo,
            }
        },
        getters: {
            allTags(): DataTags {
                return this.database.allTags();
            },
        },
        actions: {
            clearUserInfo(){
                this.user = {
                    id: 0,
                    username: '',
                    enc_key: '',
                    name: '',
                    is_admin: false,
                    mandatory_tags: [],
                    has_avatar: false,
                    max_storage: 0,
                };
            },
            // reload the database from backend
            reload(
                onStart: () => void = () => {this.database.clear()},
                onSuccess: () => void = () => {}, 
                onError: (err: Error) => void = () => {}, 
                ){

                onStart()
                function __requestDBData( dStore: ReturnType<typeof useDataStore>,){
                    // dStore.database.requestData().then(
                    dStore.database.init().then(
                        (_)=>{ onSuccess(); },
                        (err)=>{ onError(err); }
                    )
                }
                __requestDBData(this);
            },
        }

    }
)

export const useSettingsStore = defineStore(
    "settings", {
        state: () => {
            return {
                __encKey: (()=>{
                    // backward compatibility, before v1.7.2, the encKey was stored in localStorage
                    // now it is stored in cookie
                    const oldKey = localStorage.getItem("encKey");
                    if (oldKey){
                        localStorage.removeItem("encKey");
                        setCookie("encKey", oldKey, 1);
                        return oldKey;
                    }
                    // return the encKey from cookie
                    return getCookie("encKey");
                })(),
                __showTagPanel: (localStorage.getItem("showTagPanel") || String(window.innerWidth > 768)) === "true",
                __showHomeInfoPanel: (localStorage.getItem("showHomeInfoPanel") || "false") === "true",
                __show3DScatterPlot: (localStorage.getItem("show3DScatterPlot") || "false") === "true",
                __readerLayoutType: localStorage.getItem("readerLayoutType") || "2",
                __numItemsPerPage: localStorage.getItem("numItemsPerPage") || "50",

                // backend host and port are stored in sessionStorage, 
                // unless user change it manually when login or via url parameters, 
                // this is to make sure that the application always prioritize the backend on the same server.
                __backendHost: sessionStorage.getItem("backendUrl") || defaultBackendHost(),
                __backendPort: sessionStorage.getItem("backendPort") || defaultBackendPort(),

                // loggedIn is a watched flag by App.vue, which is used for logout / reload database
                loggedIn: false,    
            }
        },
        "getters":{
            encKey(): string{
                return this.__encKey;
            },
            backendHost(): string{
                return this.__backendHost;
            },
            backendPort(): string{
                return this.__backendPort;
            },
            showTagPanel(): boolean{
                return this.__showTagPanel;
            },
            showHomeInfoPanel(): boolean{
                return this.__showHomeInfoPanel;
            },
            show3DScatterPlot(): boolean{
                return this.__show3DScatterPlot;
            },
            readerLayoutType(): number{
                return parseInt(this.__readerLayoutType);
            },
            numItemsPerPage(): number{
                return parseInt(this.__numItemsPerPage);
            }
        },
        "actions": {
            setEncKey(key: string, keep: boolean | undefined = undefined){
                if (keep === undefined){
                    keep = isCookieKept("encKey");
                }
                this.__encKey = key;
                setCookie("encKey", key, keep? 7: null);
            },
            setBackendHost(url: string){
                this.__backendHost = url;
                sessionStorage.setItem("backendUrl", url);
            },
            setBackendPort(port: string){
                this.__backendPort = port;
                sessionStorage.setItem("backendPort", port);
            },
            setShowTagPanel(show: boolean){
                this.__showTagPanel = show;
                localStorage.setItem("showTagPanel", show.toString());
            },
            setShowHomeInfoPanel(show: boolean){
                this.__showHomeInfoPanel = show;
                localStorage.setItem("showHomeInfoPanel", show.toString());
            },
            setShow3DScatterPlot(show: boolean){
                this.__show3DScatterPlot = show;
                localStorage.setItem("show3DScatterPlot", show.toString());
            },
            setReaderLayoutType(type: number){
                this.__readerLayoutType = type.toString();
                localStorage.setItem("readerLayoutType", type.toString());
            },
            setNumItemsPerPage(num: number){
                this.__numItemsPerPage = num.toString();
                localStorage.setItem("numItemsPerPage", num.toString());
            },

            // no corresponding setter for the following getter
            backend(): string {
                return `${this.backendHost}:${this.backendPort}`
            }
        },
    }
)

function defaultBackendHost(){
    let BACKEND_PROTOCAL: 'http:' | 'https:' = window.location.protocol as 'http:' | 'https:';
    let HOSTNAME = window.location.hostname;
    return `${BACKEND_PROTOCAL}//${HOSTNAME}`;
}

function defaultBackendPort(){
    const windowPort = window.location.port;
    if (windowPort === "1420"){
        // Development mode.
        // the backend is separated from the frontend in development mode
        // by default, the backend is running on port 8080
        // the frontend is running on port 1420 with `npm run dev`
        return "8080";
    }
    else{
        // Production mode.
        // the backend is running on the same port as the frontend
        return windowPort;
    }
}