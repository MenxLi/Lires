import type { DataInfoT } from "./protocalT";
import { ServerConn } from "./serverConn";

export class TagRule {
    sep = "->";
    allParentsOf(tag: string): string[]{
        const splitted = tag.split(this.sep);
        return splitted;
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
