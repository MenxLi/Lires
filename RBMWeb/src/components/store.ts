
import { defineStore } from 'pinia'
import { DataBase, DataSearcher, DataPoint, DataTags } from '../core/dataClass'
import { ServerConn } from '../core/serverConn'
import { formatAuthorName } from '../libs/misc'
export { formatAuthorName }
import { platformType } from '../config'
import type { SearchStatus, PopupStyle, TagStatus } from './interface'
import type { AccountPermission } from '../core/protocalT'

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
            }
        },
        getters: {
            // tagSelectionState(): Record<string, boolean> {
            //     const ret: Record<string, boolean> = {};
            //     const allTags = useDataStore().database.getAllTags();
            //     allTags.forEach(tag => ret[tag] = tag in this.currentlySelectedTags);
            //     console.log(ret)
            //     return ret;
            // }
        },
        actions: {
            updateShownData(){
                // update shownDataUIDs, which is used to control the display of data cards
                // Should call this function manually, because it involves async operation (searching)
                const dataStore = useDataStore();
                this.tagStatus.all = dataStore.allTags;
                const tagFilteredDataPoints = dataStore.database.getDataByTags(this.tagStatus.checked);
                DataSearcher.filter(tagFilteredDataPoints, this.searchState).then(
                    (datapoints: DataPoint[]) => this.shownDataUIDs = datapoints.map((dp) => dp.summary.uuid)
                )
            },
            addRecentlyReadDataUID(uid: string){
                if (useDataStore().database.get(uid).isDummy()){
                    return;
                }
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
            }
        }
    }
)

export const useDataStore = defineStore(
    "data", {
        state: () => {
            return {
                database: new DataBase(),
            }
        },
        getters: {
            authorPublicationMap(): Record<string, DataPoint[]> {
                const ret: Record<string, DataPoint[]> = {};
                console.log("Generating authorPublicationMap...") // debug
                for (const data of this.database){
                    for (let author of data.summary.authors){
                        author = formatAuthorName(author);
                        if (!(author in ret)){
                            ret[author] = [];
                        }
                        ret[author].push(data);
                    }
                }
                return ret;
            },
            allTags(): DataTags {
                return this.database.getAllTags();
            }
        },
        actions: {
            // reload the database from backend
            reload(
                backendReload: boolean = false,
                onSuccess: () => void = () => {}, 
                onError: (err: Error) => void = () => {}, 
                clearHook: () => void = () => {},
                ){
                this.database.clear();
                // clearHook is used to update the UI status
                clearHook();

                function __requestDBData( dStore: ReturnType<typeof useDataStore>,){
                    dStore.database.requestData().then(
                        (_)=>{ onSuccess(); },
                        (err)=>{ onError(err); }
                    )
                }

                if (backendReload){
                    new ServerConn().reqReloadDB().then(
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
                __encKey: localStorage.getItem("encKey") || "",
                __backendUrl: localStorage.getItem("backendUrl") || defaultBackendHost(),
                __backendPort: localStorage.getItem("backendPort") || "8080",
                __showTagPanel: (localStorage.getItem("showTagPanel") || "true") === "true",
                loggedIn: false,    // will be watched by App.vue to reload the database
                accountPermission: null as AccountPermission | null,
            }
        },
        "getters":{
            encKey(): string{
                return this.__encKey;
            },
            backendUrl(): string{
                return this.__backendUrl;
            },
            backendPort(): string{
                return this.__backendPort;
            },
            showTagPanel(): boolean{
                return this.__showTagPanel;
            }
        },
        "actions": {
            setEncKey(key: string, keep: boolean | null){
                this.__encKey = key;
                if (keep === true){
                    localStorage.setItem("encKey", key);
                }
                else if (keep === false){
                    localStorage.removeItem("encKey");
                }
            },
            setBackendUrl(url: string){
                this.__backendUrl = url;
                localStorage.setItem("backendUrl", url);
            },
            setBackendPort(port: string){
                this.__backendPort = port;
                localStorage.setItem("backendPort", port);
            },
            setShowTagPanel(show: boolean){
                this.__showTagPanel = show;
                localStorage.setItem("showTagPanel", show.toString());
            }
        },
    }
)

function defaultBackendHost(){
    let BACKEND_PROTOCAL: 'http:' | 'https:' = window.location.protocol as 'http:' | 'https:';
    let HOSTNAME = window.location.hostname;
    if (platformType() === "tauri"){
        if (!import.meta.env.DEV){
            // assume the backend is https in tauri production mode, 
            // because we've used broswer fetch api for api requests
            // however tauri use native webview, which can not access http backend
            // the backend should be deployed on the server with ssl certificate
            BACKEND_PROTOCAL = "https:";     
            // set fixed host, may be changed in the future
            HOSTNAME = "limengxun.com";
        }
    }
    return `${BACKEND_PROTOCAL}//${HOSTNAME}`;
}