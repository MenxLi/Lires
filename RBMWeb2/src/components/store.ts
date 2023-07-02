
import { defineStore } from 'pinia'
import { DataBase, DataSearcher, DataPoint, DataTags } from '../core/dataClass'
import { formatAuthorName } from '../libs/misc'
export { formatAuthorName }
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
                // TEST
                // popupValues : {
                //     "1": {
                //         content: "This is an alert",
                //         styleType: "alert",
                //     },
                //     "2": {
                //         content: "This is a warning",
                //         styleType: "warning",
                //     },
                //     "3": {
                //         content: "This is a info",
                //         styleType: "info",
                //     },
                //     "4": {
                //         content: "This is a success",
                //         styleType: "success",
                //     },
                // } as Record<string, PopupValue>,
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
        }
    }
)

export const useSettingsStore = defineStore(
    "settings", {
        state: () => {
            return {
                __encKey: localStorage.getItem("encKey") || "",
                accountPermission: null as AccountPermission | null,
                backendPort: "8080",
            }
        },
        "getters":{
            encKey(): string{
                return this.__encKey;
            }
        },
        "actions": {
            setEncKey(key: string, keep: boolean){
                this.__encKey = key;
                if (keep){
                    localStorage.setItem("encKey", key);
                }
            }
        },
    }
)