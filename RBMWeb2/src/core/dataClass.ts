import type { DataInfoT } from "./protocalT";
import { ServerConn } from "./serverConn";
import { getBackendURL } from "@/config";

export interface TagHierarchy extends Record<string, TagHierarchy>{};
export const TAG_SEP = "->";

export class TagRule {
    static allParentsOf(tag: string): string[]{
        return [];
    }

    static tagHierarchy(tags: string[]): TagHierarchy{
        const SEP = TAG_SEP;

        function splitFirstElement(tag: string, sep: string): [string, string] | [string]{
            const splitted = tag.split(sep);
            if (splitted.length === 1) {return [tag]};
            return [splitted[0], splitted.slice(1, ).join(sep)]
        }

        // Turn a list of tags into TagHierarchy objects without parents
        function disassemble(tags: string[], sep: string = SEP): TagHierarchy{
            const interm: Record<string, string[]> = {}
            const splittedTags = tags.map((tag) => splitFirstElement(tag, sep))
            for (const st of splittedTags){
                if (!(st[0] in interm)){
                    interm[st[0]] = [];
                }
                if (st.length === 2){
                    interm[st[0]].push(st[1]);
                }
            }
            const res: TagHierarchy = {};
            for (const key in interm){
                res[key] = disassemble(interm[key], sep);
            }
            return res;
        }

        // Aggregately add parent portion of the hierarchy, in-place operation
        function assemble(disassembled: TagHierarchy, sep: string = SEP): TagHierarchy{
            for (const key in disassembled){
                const value = disassembled[key];
                for (const childKey in value){
                    const newKey = [key, childKey].join(SEP);
                    value[newKey] = value[childKey];
                    delete value[childKey];
                }
                assemble(value, sep);
            }
            return disassembled;
        }
        return assemble(disassemble(tags));
    }

    static isSubset(query: Array<string>, value: Array<string>): boolean{
        let flag = true;
        for (const q of query){
            if (!(value.includes(q))){
                flag = false;
                break;
            }
        }
        return flag;
    }
}

export class DataPoint {
    info: DataInfoT;
    constructor(summary: DataInfoT) {
        this.info = summary;
    }

    authorAbbr(): string {
        let end = "";
        if (this.info.authors.length > 1) {
            end = " et al.";
        }
        return this.info.authors[0] + end;
    }

    authorYear(): string{
        return `${this.authorAbbr()} ${this.info.year}`
    }

    getOpenDocURL(): string {
        const uid = this.info.uuid;
        if (this.info["has_file"] && this.info["file_type"] == ".pdf"){
            return `${getBackendURL()}/doc/${uid}`
        }
        if (this.info["has_file"] && this.info["file_type"] == ".hpack"){
            return `${getBackendURL()}/hdoc/${uid}`
        }
        if (!this.info["has_file"] && this.info["url"]){
            return this.info.url;
        }
        return ""
    }
}

export class DataBase {
    data: Record<string, DataPoint>;

    constructor(){
        this.data = {}
    }

    *[Symbol.iterator](): Iterator<DataPoint>{
        for (let uid in this.data){
            yield this.data[uid];
        }
    }

    async requestData(){
        const conn = new ServerConn();
        const allData = await conn.reqFileList([]);
        for ( let summary of allData ){
            this.add(summary);
        }
    }

    add(summary: DataInfoT): void {
        this.data[summary.uuid] = new DataPoint(summary);
    }

    get(uuid: string): DataPoint{
        return this.data[uuid];
    }

    getAllTags() : Set<string> {
        let _tags: string[];
        // let all_tags: Set<string> = new Set(["hello", "world"]);
        let all_tags: Set<string> = new Set();
        for (const data of this){
            _tags = data.info["tags"];;
            for (const t of _tags){
                all_tags.add(t);
            }
        }
        return all_tags;
    }

    getUidByTags(tags: string[]): string[] {
        const valid_data = [];
        for (const uid in this.data){
            const data = this.data[uid];
            const data_tag = data.info["tags"];
            if (TagRule.isSubset(tags, data_tag)) {
                valid_data.push(data.info.uuid)
            }
        }
        return valid_data;
    }
}
