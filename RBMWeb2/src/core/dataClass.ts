import type { DataInfoT } from "./protocalT";
import { ServerConn } from "./serverConn";

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
}
