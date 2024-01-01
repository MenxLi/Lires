
import { defineStore } from 'pinia'
import { DataBase, DataSearcher, DataPoint, DataTags } from '../core/dataClass'
import { ServerConn } from '../core/serverConn'
import { formatAuthorName } from '../libs/misc'
export { formatAuthorName }
import type { SearchStatus, PopupStyle, TagStatus } from './interface'
import type { UserInfo } from '../core/protocalT'

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
                }

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
                this.tagStatus.all = dataStore.allTags;
                const tagFilteredDataPoints = dataStore.database.getDataByTags(this.tagStatus.checked);
                DataSearcher.filter(tagFilteredDataPoints, this.searchState).then(
                    // (datapoints: DataPoint[]) => this.shownDataUIDs = datapoints.map((dp) => dp.summary.uuid)
                    (filterRes) => {
                        this.shownDataUIDs = filterRes.datapoints.map((dp) => dp.summary.uuid)
                        this.shownDataScores = filterRes.scores;
                    }
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
            },
            reloadDatabase(
                backendReload: boolean = false,
            ){
                useDataStore().reload(
                    backendReload,
                    () => {
                        this.databaseLoadingStatus.nCurrent = 0;
                        useDataStore().database.clear();
                        this.updateShownData()
                    },
                    () => {
                        this.updateShownData(); 
                        useUIStateStore().databaseLoadingStatus.nTotal = -1
                    },
                    () => {
                        this.showPopup(`Failed to load database from: ${new ServerConn().apiURL()}`, "alert");
                        useUIStateStore().databaseLoadingStatus.nTotal = -1
                    },
                    (nCurrent, nTotal) => {
                        this.databaseLoadingStatus.nCurrent = nCurrent;
                        this.databaseLoadingStatus.nTotal = nTotal
                    }
                )

            }
        }
    }
)

export const useDataStore = defineStore(
    "data", {
        state: () => {
            return {
                database: new DataBase(),
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
                uiUpdateCallback: (nCurrent_: number, nTotal_: number) => void = () => {},
                ){

                onStart()
                function __requestDBData( dStore: ReturnType<typeof useDataStore>,){
                    // dStore.database.requestData().then(
                    dStore.database.requestDataStream(uiUpdateCallback).then(
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
                __encKey: localStorage.getItem("encKey") || sessionStorage.getItem("encKey") || "",
                __showTagPanel: (localStorage.getItem("showTagPanel") || "true") === "true",
                __show3DScatterPlot: (localStorage.getItem("show3DScatterPlot") || "false") === "true",
                __readerLayoutType: localStorage.getItem("readerLayoutType") || "2",

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
        },
        "actions": {
            setEncKey(key: string, keep: boolean | null){
                this.__encKey = key;
                if (keep === true){
                    localStorage.setItem("encKey", key);
                }
                else{
                    if (localStorage.getItem("encKey")){
                        // make sure it won't be obtained from local storage
                        localStorage.removeItem("encKey");
                    }
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
        },
    }
)

function defaultBackendHost(){
    let BACKEND_PROTOCAL: 'http:' | 'https:' = window.location.protocol as 'http:' | 'https:';
    let HOSTNAME = window.location.hostname;
    return `${BACKEND_PROTOCAL}//${HOSTNAME}`;
}

function defaultBackendPort(){
    return window.location.port;
}