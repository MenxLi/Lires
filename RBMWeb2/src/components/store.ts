
import { defineStore } from 'pinia'

export const useTagSelectionStore = defineStore(
    "tagSelection", {
        state: () => {
            return {
                currentlySelected: [] as string[]
            }
        }
    }
)

export const useDataStore = defineStore(
    "data", {
        state: () => {
            return {
                selectorShownUIDs: [] as string[]
            }
        }
    }
)