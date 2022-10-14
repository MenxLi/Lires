import {DataInfoT} from "./protocalT.js";
import {getLogger} from "./libs/logging.js"

class DataFilter{
    db: DataInfoT[];

    constructor(allData: DataInfoT[]){
        this.db = allData;
    }

    *[Symbol.iterator](){
        for (let d of this.db){
            yield d;
        }
    }

    getDataKeys(): string[] {
        return Array.from(Object.keys(this.db[0]))
    }

    getAllTags() : Set<string> {
        let _tags: string[];
        let all_tags: Set<string> = new Set();
        for (const data of this.db){
            _tags = data["tags"];;
            for (const t of _tags){
                all_tags.add(t);
            }
        }
        return all_tags;
    }

    getDataByUUID (uuid: string): DataInfoT|null{
        for (const data of this.db){
            if (data["uuid"] === uuid){
                return data
            }
        }
        return null;
    }

    static filterBySearch(datalist: DataInfoT[], field: string, pattern: string): DataInfoT[]{
        if (!pattern){
            return datalist;
        }
        const dl_new = new Array();
        for (const d of datalist){
            const value: any = (d as any)[field];

            if (Array.isArray(value)){
                for (const _v of value){
                    if (_v.search(pattern) !== -1){ dl_new.push(d); break;}
                }
            }
            else if (typeof(value) == "string") {
                if (value.search(pattern) !== -1){ dl_new.push(d); }
            }
            else {
                getLogger("rbm").error(`Invalid value type: ${typeof(value)}`)
                getLogger("rbm").debug(`get invalid value while fitering by search: ${value}`)
            }
        }
        return dl_new;
    }

    static filterByTag(datalist: DataInfoT[], tags: string[]): DataInfoT[]{
        const valid_data = [];
        for (const data of datalist){
            const data_tag = data["tags"];
            if (isSubset(tags, data_tag)) {
                valid_data.push(data)
            }
        }
        return valid_data;
    }

}

function isSubset(query: string[], value: string[]): boolean{
    let flag = true;
    for (const q of query){
        if (!(value.includes(q))){
            flag = false;
            break;
        }
    }
    return flag;
}


export {DataFilter}
