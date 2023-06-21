// Type definitions across components

import type { DataPoint, DataTags } from "../core/dataClass"

export interface TagStatus{
    checked: DataTags,
    all: DataTags,
    unfolded: DataTags
}

export interface SearchStatus{
    searchBy: string,
    content: string
}

export interface DataCardsStatus{
    datapoints: DataPoint[],
    unfoldedIds?: string[]
}

export type PopupStyle = "alert" | "error" | "warning" | "info" | "success"