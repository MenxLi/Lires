// Type definitions across components

import type { DataTags } from "../core/tag"

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

export interface PlotPoints3D {
    x: number[] | Float32Array;
    y: number[] | Float32Array;
    z: number[] | Float32Array;
    text: string[];
    color: string | string[] | null;
    opacity: number;
}