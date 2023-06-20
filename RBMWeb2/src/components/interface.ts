// Type definitions across components

import type { DataTags } from "../core/dataClass"

export interface TagStatus{
    checked: DataTags,
    all: DataTags,
    unfolded: DataTags
}

export interface SearchStatus{
    searchBy: string,
    content: string
}

export type PopupStyle = "alert" | "error" | "warning" | "info" | "success"