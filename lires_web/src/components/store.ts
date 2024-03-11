
import { defineStore } from 'pinia'
import { DataBase } from '../core/dataClass'
import { UserPool } from '../core/user'
import { DataTags } from '../core/tag'
import { ServerConn } from '../api/serverConn'
import { ServerWebsocketConn } from '../api/serverWebsocketConn'
import { formatAuthorName } from '../utils/misc'
export { formatAuthorName }
import type { SearchStatus, PopupStyle, TagStatus } from './interface'
import type { UserInfo } from '../api/protocalT'

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
                        "searchBy": "",
                        "content": ""
                    } as SearchStatus,
                unfoldedDataUIDs: [] as string[],

                // reader component
                recentlyReadDataUIDs: [] as string[],
                preferredReaderLeftPanelWidthPerc: 0.65,

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

            }
        },
        actions: {
            updateShownData(){
                // update shownDataUIDs, which is used to control the display of data cards
                // Should call this function manually, because it involves async operation (searching)
                const dataStore = useDataStore();
                this.tagStatus.all = dataStore.allTags;     // in case tag pool are updated from the backend
                console.log("DEBUG: updateShownData() is called.")
                useConnectionStore().conn.filter(
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
            reloadDatabase(
                backendReload: boolean = false,
            ){
                useDataStore().reload(
                    backendReload,
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
            return {
                conn: new ServerConn(
                    useSettingsStore().backend,
                    () => useSettingsStore().encKey
                ),
                wsConn: new ServerWebsocketConn(
                    useSettingsStore().backend,
                    () => useSettingsStore().encKey
                )
            }
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
                };
            },
            // reload the database from backend
            reload(
                backendReload: boolean = false,
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

                if (backendReload){
                    // should be deprecated...
                    useConnectionStore().conn.reqReloadDB().then(
                        (success) => {
                            console.log("Reload: ", success);
                            if (success){ __requestDBData(this); }
                            else{ onError(new Error("Failed to reload database from backend")); }
                        },
                        (err) => { onError(err); }
                    )
                }
                else{ __requestDBData(this); }
            },
        }

    }
)

export const useSettingsStore = defineStore(
    "settings", {
        state: () => {
            return {
                __encKey: sessionStorage.getItem("encKey") || localStorage.getItem("encKey") || "",
                __showTagPanel: (localStorage.getItem("showTagPanel") || "true") === "true",
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
            setEncKey(key: string, keep: boolean){
                this.__encKey = key;
                if ( keep === true){
                    localStorage.setItem("encKey", key);
                }
                else {
                    // clear the encKey in local storage if keep is false
                    if (localStorage.getItem("encKey")){
                        localStorage.removeItem("encKey");
                    }
                    // set the encKey in sessionStorage as a one-time token
                    sessionStorage.setItem("encKey", key);
                }
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