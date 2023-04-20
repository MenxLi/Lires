
import { defineStore } from 'pinia'
import { DataBase, DataSearcher, DataPoint } from '@/core/dataClass'
import type { SearchStatus } from './_interface'

export const useUIStateStore = defineStore(
    "uiStatus", {
        state: () => {
            return {
                currentlySelectedTags: [] as string[],
                shownDataUIDs: [] as string[],
                searchState: {
                        "content": ""
                    } as SearchStatus,
            }
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