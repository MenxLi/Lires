
import { defineStore } from 'pinia'
import { DataBase, DataSearcher, DataPoint, DataTags } from '../core/dataClass'
import type { SearchStatus } from './home/_interface'
import { formatAuthorName } from '../libs/misc'
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
                        // // the author name may be in the form of <Given Name> <...> <Family Name>
                        // // make sure formatted author is named as <Family Name>, <Given Name>
                        // if (author.indexOf(',') === -1){
                        //     const names = author.split(' ');
                        //     author = names[names.length - 1] + ', ' + names.slice(0, names.length - 1).join(' ');
                        //     author = author.trim().toLowerCase();
                        // }
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