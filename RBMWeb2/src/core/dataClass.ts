import type { DataInfoT, SearchResultant } from "./protocalT";
import { ServerConn } from "./serverConn";
import { getBackendURL } from "../config";
import type { SearchStatus } from "../components/_interface";

export interface TagHierarchy extends Record<string, TagHierarchy>{};
export const TAG_SEP = "->";

export class DataTags extends Set<string>{
    union( tags: DataTags){
        const ret = new DataTags(this)
        ret.union_(tags);
        return ret;
    }
    union_(tags: DataTags){
        tags.forEach((value) => this.add(value));
        return this;
    }
    pop( tags: DataTags){
        const ret = new DataTags(this);
        ret.pop_(tags);
        return ret;
    }
    pop_(tags: DataTags){
        tags.forEach((value) => this.delete(value));
        return this;
    }
    issubset(tags: DataTags){
        return TagRule.isSubset(this, tags)
    }
    withParents():DataTags {
        const ret = new DataTags(this)
        this.forEach(tag => ret.union_(TagRule.allParentsOf(tag)));
        return ret;
    }
    withChildsFrom(tagPool: DataTags): DataTags{
        const ret = new DataTags(this)
        tagPool.forEach((tag) => ret.union_(TagRule.allChildsOf(tag, tagPool)));
        return ret;
    }
}

export class TagRule {
    // assume cls.SEP is '.'
    // input: a.b.c
    // return: [a, a.b]
    static allParentsOf(tag: string): DataTags {
        const sp = tag.split(TAG_SEP);
        if (sp.length === 1) {
          return new DataTags([]);
        }
        const accum = [];
        const all_p_tags = [];
        for (let i = 0; i < sp.length - 1; i++) {
          accum.push(sp[i]);
          all_p_tags.push(accum.join(TAG_SEP));
        }
        return new DataTags(all_p_tags);
      }

    // assume cls.SEP is '.'
    // input: (a.b, [a, a.b, a.b.c, a.b.d])
    // return: [a.b.c, a.b.d]
    static allChildsOf(tag: string, tag_pool: DataTags): DataTags {
        const ret = new DataTags();
        for (const t of tag_pool) {
          if (t.startsWith(tag) && t.length > tag.length + TAG_SEP.length) {
            if (t.substring(tag.length, tag.length + 1 + TAG_SEP.length) === `${TAG_SEP}`) {
              ret.add(t);
            }
          }
        }
        return ret;
    }

    static tagHierarchy(tags: DataTags): TagHierarchy{
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
        return assemble(disassemble(Array.from(tags)));
    }

    static isSubset(query: DataTags, value: DataTags): boolean{
        let flag = true;
        for (const q of query){
            if (!(value.has(q))){
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

    yearAuthor(hyphen=" "): string{
        return `${this.info.year}${hyphen}${this.authorAbbr()}`
    }

    getOpenDocURL(): string {
        const uid = this.info.uuid;
        if (this.info["has_file"] && this.info["file_type"] == ".pdf"){
            return `${getBackendURL()}/doc/${uid}`
        }
        if (this.info["has_file"] && this.info["file_type"] == ".hpack"){
            return `${getBackendURL()}/hdoc/${uid}/`
        }
        if (!this.info["has_file"] && this.info["url"]){
            return this.info.url;
        }
        return ""
    }

    getOpenNoteURL(): string {
        const uid = this.info.uuid;
        return `${getBackendURL()}/comment/${uid}/`;
    }

    docType(): "" | "pdf" | "url" | "hpack" | "unknown" {
        if (this.info["has_file"] && this.info["file_type"] == ".pdf"){
            return "pdf";
        }
        else if (this.info["has_file"] && this.info["file_type"] == ".hpack"){
            return "hpack";
        }
        else if (!this.info["has_file"] && this.info["url"]){
            return "url";
        }
        else if (!this.info["has_file"] && !this.info["url"]){
            return "";
        }
        else {
            return "unknown";
        }
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

    getAllTags() : DataTags {
        let _tags: string[];
        // let all_tags: Set<string> = new Set(["hello", "world"]);
        let all_tags: Set<string> = new Set();
        for (const data of this){
            _tags = data.info["tags"];;
            for (const t of _tags){
                all_tags.add(t);
            }
        }
        return new DataTags(all_tags);
    }

    getDataByTags(tags: string[]| DataTags): DataPoint[] {
        tags = new DataTags(tags);
        const valid_data = [];
        for (const uid in this.data){
            const data = this.data[uid];
            const data_tag = new DataTags(data.info["tags"]);
            if (tags.issubset(data_tag.withParents())) {
                valid_data.push(data)
            }
        }
        return valid_data;
    }
}


export class DataSearcher{

    // perform a search and sort on the datapoints
    static async filter(datapoints: DataPoint[], searchStatus: SearchStatus): Promise<DataPoint[]> {
        const pattern = searchStatus["content"].toLowerCase();
        if (!pattern){
            return this.sortDefault(datapoints, false);
        }
        const valid_uids = new Set();
        for (const dp of datapoints){
            valid_uids.add(dp.info.uuid);
        }

        const dp_new: DataPoint[] = new Array();

        // server search
        if (searchStatus.searchBy.toLowerCase() === "feature"){
            const conn = new ServerConn();
            const res = await conn.search("searchFeature", {"pattern": searchStatus.content , "n_return": 999});
            const scores: number[] = new Array();
            for (const dp of datapoints){
                if (res[dp.info.uuid]){
                    dp_new.push(dp);
                    const score = (res[dp.info.uuid] as SearchResultant).score as number;   // score exists on feature search
                    scores.push(score);
                }
            }

            return this.sortByScore(dp_new, scores, false);
        } 

        // local search
        if (searchStatus.searchBy.toLowerCase() === "title"){
            for (const dp of datapoints){
                if (dp.info.title.toLowerCase().search(pattern) !== -1){
                    dp_new.push(dp);
                }
            }
        }
        else if (searchStatus["searchBy"].toLowerCase() === "general"){
            for (const dp of datapoints){
                const toSearch = `${dp.info.title}|${dp.info.authors.join(", ")}|${dp.info.year}`.toLowerCase()
                if (toSearch.search(pattern) !== -1){ dp_new.push(dp); }
            }
        }
        else{
            throw new Error("Unknown searchBy option");
        }
        return this.sortDefault(dp_new, false);
    }

    // sort datapoints by default method, the later added, the first (descending order)
    static sortDefault(datapoints: DataPoint[], reverse = false): DataPoint[]{
        if (reverse){
            return datapoints.sort((a, b) => a.info.time_added - b.info.time_added)
        }
        return datapoints.sort((b, a) => a.info.time_added - b.info.time_added)
    }

    // return a list of datapoints that are sorted by scores
    // - reverse: if false, sort in descending order
    static sortByScore<T>(arr: T[], scores: number[], reverse = false): T[]{
        if (arr.length !== scores.length){
            throw new Error("arr.length !== scores.length");
        }

        const arr_score = new Array();
        for (let i = 0; i < arr.length; i++){
            arr_score.push([arr[i], scores[i]]);
        }

        let arr_score_sorted;
        if (reverse){
            arr_score_sorted = arr_score.sort((a, b) => a[1] - b[1]);
        }
        else{
            arr_score_sorted = arr_score.sort((a, b) => b[1] - a[1]);
        }

        const ret = new Array();
        for (const item of arr_score_sorted){
            ret.push(item[0]);
        }

        return ret;
    }
}