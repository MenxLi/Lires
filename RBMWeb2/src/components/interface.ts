// Type definitions across components

export interface TagCheckStatus{
    identifier: string,
    isChecked: boolean,
    currentlySelected: string[]
}

export interface SearchStatus{
    searchBy: string,
    content: string
}

export type PopupStyle = "alert" | "warning" | "info" | "success"