
import { defineStore } from 'pinia'
import { DataBase, DataSearcher, DataPoint, DataTags } from '@/core/dataClass'
import type { SearchStatus } from './_interface'

export const useUIStateStore = defineStore(
    "uiStatus", {
        state: () => {
            return {
                currentlySelectedTags: new DataTags(),
                unfoldedTags: new DataTags(),
                shownDataUIDs: [] as string[],
                searchState: {
                        "content": ""
                    } as SearchStatus,
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
                    (datapoints: DataPoint[]) => this.shownDataUIDs = datapoints.map((dp) => dp.info.uuid)
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
        }
    }
)