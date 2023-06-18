
import { defineStore } from 'pinia'
import { DataBase, DataSearcher, DataPoint, DataTags } from '../core/dataClass'
import type { SearchStatus } from './home/_interface'
import { formatAuthorName } from '../libs/misc'
import Popup from './common/Popup.vue'
export { formatAuthorName }

export const useUIStateStore = defineStore(
    "uiStatus", {
        state: () => {
            return {
                currentlySelectedTags: new DataTags(),
                unfoldedTags: new DataTags(),
                shownDataUIDs: [] as string[],
                searchState: {
                        "searchBy": "",
                        "content": ""
                    } as SearchStatus,
                unfoldedDataUIDs: [] as string[],

                // global popup component, need to be initialized in App.vue
                popupRef: null as null | typeof Popup,
                popupValue : {
                    show: false,
                    style: "alert",
                    content: "",
                },

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
                // update shownDataUIDs
                const dataStore = useDataStore();
                const tagFilteredDataPoints = dataStore.database.getDataByTags(this.currentlySelectedTags);
                DataSearcher.filter(tagFilteredDataPoints, this.searchState).then(
                    (datapoints: DataPoint[]) => this.shownDataUIDs = datapoints.map((dp) => dp.summary.uuid)
                )
            },
            showPopup(
                content: string, 
                style: string = "info",
                time: number = 2000     // in ms
                ){
                this.popupValue = {
                    show: true,
                    style: style,
                    content: content,
                }
                // hide after some time
                setTimeout(() => {
                    this.popupValue.show = false;
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
            }
        }
    }
)