import type { DataInfoT, SearchResultant } from "../api/protocalT";
import { ServerConn } from "../api/serverConn";
import { getBackendURL } from "../config";
import type { SearchStatus } from "../components/interface";
import { useSettingsStore, useDataStore, formatAuthorName } from "../components/store";
import { DataTags } from "./tag";

function apiURL(){
    return `${getBackendURL()}/api`;
}


export class DataPoint {
    summary: DataInfoT;
    supp: Record<'note' | 'abstract', string | null>;

    constructor(summary: DataInfoT) {
        this.summary = summary;
        // supplimentary information for this datapoint,
        // need to fetch from server
        // it is designed to be a lazy fetch to save bandwidth
        this.supp = {
            note: null,
            abstract: null,
        }
    }

    get tags(): DataTags{
        return new DataTags(this.summary.tags);
    }

    toString(){
        return `${this.summary.title} - ${this.authorAbbr()} (${this.summary.year}) [uid: ${this.summary.uuid}]`
    }

    // will update this.supp.abstract
    fetchAbstract(): Promise<string> {
        return new Promise((resolve, reject) => {
            new ServerConn().reqDatapointAbstract(this.summary.uuid).then((data) => {
                this.supp.abstract = data;
                resolve(data);
            }).catch((err) => {
                reject(err);
            })
        })
    }

    // will update this.supp.abstract and upload to server
    uploadAbstract(abstract: string): Promise<boolean> {
        return new Promise((resolve, reject) => {
            if (abstract === this.supp.abstract || abstract === null) {
                resolve(true);
                return;
            }
            new ServerConn().reqDatapointAbstractUpdate(this.summary.uuid, abstract).then((data) => {
                this.supp.abstract = abstract;
                resolve(data);
            }).catch((err) => {
                reject(err);
            })
        })
    }

    // will update this.supp.note
    fetchNote(): Promise<string> {
        return new Promise((resolve, reject) => {
            new ServerConn().reqDatapointNote(this.summary.uuid).then((data) => {
                this.supp.note = data;
                resolve(data);
            }).catch((err) => {
                reject(err);
            })
        })
    }

    // will update this.supp.note and upload to server
    uploadNote(note: string): Promise<boolean> {
        if (note === null) {
            return Promise.reject("Note is null");
        }
        // replace image url with ./misc/
        note = note.replace(new RegExp(`${getBackendURL()}/img/${this.summary.uuid}\\?fname=`, 'g'), './misc/');
        return new Promise((resolve, reject) => {
            new ServerConn().reqDatapointNoteUpdate(
                this.summary.uuid,
                note as string
            ).then((data) => {
                // update local cache
                this.supp.note = note;
                this.summary.note_linecount = note.split('\n').map(
                    (line: string) => line.trim() == '' ? 0 : 1
                ).reduce((a: number, b: number) => a + b, 0);

                resolve(data);
            }).catch((err) => {
                reject(err);
            })
        })
    }

    // return a list of raw image urls
    uploadImages(images: File[]): Promise<string[]>{
        return new Promise((resolve, reject) => {
            new ServerConn().uploadImages(this.summary.uuid, images).then(
                (data) => {
                    resolve(
                        data.map((fname) => `./misc/${fname}`)
                    )
                },
                (err) => {
                    reject(err);
                }
            )
        })
    }

    uploadDocument(doc: File): Promise<DataInfoT>{
        return new ServerConn().uploadDocument(this.summary.uuid, doc);
    }
    freeDocument(): Promise<DataInfoT>{
        return new ServerConn().freeDocument(this.summary.uuid);
    }

    update(summary: null | DataInfoT = null): Promise<DataInfoT> {
        if (summary !== null) {
            this.summary = summary;
            return Promise.resolve(summary);
        }

        const res = new ServerConn().reqDatapointSummary(this.summary.uuid);
        res.then((data) => {
            this.summary = data;
        })
        return res;
    }

    destory() {
        // make this datapoint a zombie
        this.summary = _dummyDataSummary;
    }

    authorAbbr(): string {
        let end = "";
        if (this.summary.authors.length > 1) {
            end = " et al.";
        }
        return this.summary.authors[0] + end;
    }

    authorYear(): string{
        return `${this.authorAbbr()} ${this.summary.year}`
    }

    yearAuthor(hyphen=" "): string{
        return `${this.summary.year}${hyphen}${this.authorAbbr()}`
    }

    isDummy(): boolean{
        return this.summary.uuid === _dummyDataSummary.uuid;
    }

    getRawDocURL(): string {
        const uid = this.summary.uuid;
        if (this.summary["has_file"]){
            return `${getBackendURL()}/doc/${uid}`;
        }
        if (!this.summary["has_file"] && this.summary["url"]){
            return this.summary.url;
        }
        return "about:blank";
    }

    // will wrap the url with backend pdfjs viewer if the url is a pdf
    getOpenDocURL({
        extraPDFViewerParams = {} as Record<string, string>,
        urlHashMark = "" as string,
    } = {}): string {
        const backendPdfjsviewer = `${getBackendURL()}/pdfjs/web/viewer.html`;
        function _getPdfViewerURL(fURL: string, pdfjs: string = backendPdfjsviewer){
            const pdfjsviewerParams = new URLSearchParams();
            if (pdfjs === backendPdfjsviewer){
                // use backend pdfjs viewer, need to pass key
                pdfjsviewerParams.append("key", useSettingsStore().encKey)
            }
            pdfjsviewerParams.append("file", `${fURL}`);
            for (const key in extraPDFViewerParams){
                pdfjsviewerParams.append(key, extraPDFViewerParams[key]);
            }
            return `${pdfjs}?${pdfjsviewerParams.toString()}`;
        }

        function _setHashMark(url: string): string{
            if (!urlHashMark) return url

            // check if the url already has a hash mark
            const urlObj = new URL(url);
            if (urlObj.hash){
                // remove the hash mark
                url = url.slice(0, url.indexOf("#"));
            }
            return `${url}#${urlHashMark}`;
        }

        let ret = "about:blank";

        // Get the url of the document by its type
        if (this.isDummy()){
            ret = "about:blank"
        }
        if (this.summary["has_file"] && this.summary["file_type"] == ".pdf"){
            // view pdf via backend pdfjs viewer
            const pdfURL = this.getRawDocURL();
            ret = _getPdfViewerURL(_setHashMark(pdfURL));
        }
        if (this.summary["has_file"] && this.summary["file_type"] == ".html"){
            const htmlURL = this.getRawDocURL();
            ret = _setHashMark(htmlURL);
        }
        if (!this.summary["has_file"] && this.summary["url"]){
            ret = _setHashMark(this.summary.url);
        }
        console.log("Open doc url: ", ret)
        return ret;
    }

    getOpenNoteURL(): string {
        const uid = this.summary.uuid;
        return `${apiURL()}/comment/${uid}/`;
    }

    getOpenSummaryURL(): string {
        const uid = this.summary.uuid;
        return `${apiURL()}/summary?uuid=${uid}&key=${useSettingsStore().encKey}`;
    }

    docType(): "" | "html" | "pdf" | "url" | "unknown" {
        if (this.summary["has_file"] && this.summary["file_type"] == ".pdf"){
            return "pdf";
        }
        else if (this.summary["has_file"] && this.summary["file_type"] == ".html"){
            return "html";
        }
        else if (!this.summary["has_file"] && this.summary["url"]){
            return "url";
        }
        else if (!this.summary["has_file"] && !this.summary["url"]){
            return "";
        }
        else {
            return "unknown";
        }
    }
}

const _dummyDataSummary: DataInfoT = {
    has_file : false,
    file_type: "",
    year: "0000",
    title: " ",
    author: " ",
    authors: [" "],
    publication: null,
    tags: [],
    uuid: " ",
    url: "about:blank",
    time_added: 0.,
    time_modified: 0.,
    bibtex: "",
    doc_size: 0,
    note_linecount: 0,
    has_abstract: false,
}

export class DataBase {
    data: Record<string, DataPoint>;
    _initliazed: boolean;

    constructor(){
        this.data = {}
        this._initliazed = false;
    }

    get initialized(): boolean{
        return this._initliazed;
    }

    *[Symbol.iterator](): Iterator<DataPoint>{
        for (let uid in this.data){
            yield this.data[uid];
        }
    }

    async requestData(){
        const conn = new ServerConn();
        const allData = await conn.reqFileList([]);
        console.log("Get infolist of size: ", 
            (JSON.stringify(allData).length * 2 / 1024 / 1024)
            .toPrecision(2), "MB");

        this.clear();
        for ( let summary of allData ){
            this.add(summary);
        };
        this._initliazed = true;
    }

    // get the datalist in chunks
    async requestDataStream(stepCallback: (nCurrent_: number, nTotal_: number) => void = () => {}){
        const conn = new ServerConn();
        this.clear()
        await conn.reqFileListStream([], (data: DataInfoT, nCurrent: number, nTotal: number) => {
            this.add(data);
            stepCallback(nCurrent, nTotal);
        });
        console.log("Get datapoints of size: ",
            (JSON.stringify(this.data).length * 2 / 1024 / 1024)
            .toPrecision(2), "MB");
        this._initliazed = true;
    }

    add(summary: DataInfoT): DataPoint {
        this.data[summary.uuid] = new DataPoint(summary);
        return this.data[summary.uuid];
    }

    clear(){
        this.data = {};
        this._initliazed = false;
    }

    delete(uuid: string){
        delete this.data[uuid];
    }

    get(uuid: string): DataPoint{
        if (!(uuid in this.data)){
            // return a dummy data point to avoid corrupted UI update on deletion of the data.
            // A deletion may trigger UI update which refers to the deleted data via this function, and get undefined
            // I found this is tricky, but works... 
            // (The returned datapoint is temporary, after the entire UI update, the data point should be garbage collected)
            // TODO: find a better way to handle this
            return new DataPoint(_dummyDataSummary);    
        }
        return this.data[uuid];
    }

    async aget(_: string): Promise<DataPoint>{
        // will shift to async get in the future
        throw new Error("Not implemented");
    }

    getMany(uuids: string[]): DataPoint[]{
        const ret = [];
        for (const uid of uuids){
            ret.push(this.get(uid));
        }
        return ret;
    }

    getAllTags() : DataTags {
        let _tags: string[];
        let all_tags: Set<string> = new Set();
        for (const data of this){
            _tags = data.summary["tags"];;
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
            const data_tag = new DataTags(data.summary["tags"]);
            if (tags.issubset(data_tag.withParents())) {
                valid_data.push(data)
            }
        }
        return valid_data;
    }

    /**
     * @deprecated use server conn to directly rename tag,
     * and use server event to update the database and UI
     */
    async renameTag(oldTag: string, newTag: string): Promise<boolean>{
        oldTag = DataTags.removeSpaces(oldTag);
        newTag = DataTags.removeSpaces(newTag);
        const conn = new ServerConn();
        const res = await conn.renameTag(oldTag, newTag);
        if (res){
            const needUpdate = this.getDataByTags([oldTag]);
            const updateRes = await Promise.all(needUpdate.map((data) => {
                return data.update();
            }));
            return updateRes.every((x) => x);
        }
        else { return false; }
    }

    /**
     * @deprecated use server conn to directly delete tag,
     * and use server event to update the database and UI
     */
    async deleteTag(tag: string): Promise<boolean>{
        tag = DataTags.removeSpaces(tag);
        const conn = new ServerConn();
        const res = await conn.deleteTag(tag);
        if (res){
            const needUpdate = this.getDataByTags([tag]);
            const updateRes = await Promise.all(needUpdate.map((data) => {
                return data.update();
            }));
            return updateRes.every((x) => x);
        }
        else { return false; }
    }   
}


interface FilteredDataT {
    datapoints: DataPoint[],
    scores: number[] | null,
}
export class DataSearcher{

    // perform a search and sort on the datapoints
    static async filter(datapoints: DataPoint[], searchStatus: SearchStatus): Promise<FilteredDataT> {
        const pattern = searchStatus["content"].toLowerCase();
        if (!pattern){
            return {
                datapoints: this.sortDefault(datapoints, false),
                scores: null,
            }
        }
        const valid_uids = new Set();
        for (const dp of datapoints){
            valid_uids.add(dp.summary.uuid);
        }

        const dp_new: DataPoint[] = new Array();

        // server search
        if (searchStatus.searchBy.toLowerCase() === "feature"){
            const conn = new ServerConn();
            const res = await conn.search("searchFeature", {"pattern": searchStatus.content , "n_return": 999});
            const scores: number[] = new Array();
            for (const dp of datapoints){
                if (res[dp.summary.uuid]){
                    dp_new.push(dp);
                    const score = (res[dp.summary.uuid] as SearchResultant).score as number;   // score exists on feature search
                    scores.push(score);
                }
            }

            const sortedDataScore = this.sortByScore(dp_new, scores, false);
            return {
                datapoints: sortedDataScore[0],
                scores: sortedDataScore[1],
            }
        } 

        else if (searchStatus.searchBy.toLowerCase() === "note"){
            const conn = new ServerConn();
            const res = await conn.search("searchNote", {"pattern": searchStatus.content , "ignore_case": true});
            const uids = Object.keys(res);
            for (const dp of datapoints){
                if (uids.includes(dp.summary.uuid)){
                    dp_new.push(dp);
                }
            }
            return {
                datapoints: this.sortDefault(dp_new, false),
                scores: null,
            }
        }

        // local search
        else if (searchStatus.searchBy.toLowerCase() === "title"){
            for (const dp of datapoints){
                if (dp.summary.title.toLowerCase().search(pattern) !== -1){
                    dp_new.push(dp);
                }
            }
        }
        else if (searchStatus.searchBy.toLowerCase() === "uuid"){
            for (const dp of datapoints){
                if (dp.summary.uuid.toLowerCase().search(pattern) !== -1){
                    dp_new.push(dp);
                }
            }
        }
        else if (searchStatus.searchBy.toLowerCase() === "author"){
            const authorPubMap = useDataStore().authorPublicationMap;
            const searchAuthor = formatAuthorName(searchStatus.content);
            if (searchAuthor in authorPubMap){
                for (const dp of authorPubMap[searchAuthor]){
                    if (valid_uids.has(dp.summary.uuid)){
                        dp_new.push(dp);
                    }
                }
            }
            else{
                // partial input
                for (const _author in authorPubMap){
                    if (_author.search(searchAuthor) !== -1){
                        for (const dp of authorPubMap[_author]){
                            if (valid_uids.has(dp.summary.uuid)){
                                dp_new.push(dp);
                            }
                        }
                    }
                }
            }
        }
        else if (searchStatus.searchBy.toLowerCase() === "publication"){
            for (const dp of datapoints){
                if (dp.summary.publication && dp.summary.publication.toLowerCase().search(pattern) !== -1){
                    dp_new.push(dp);
                }
            }
        }
        else if (searchStatus["searchBy"].toLowerCase() === "general"){
            for (const dp of datapoints){
                const toSearch = `${dp.summary.title}|${dp.summary.authors.join(", ")}|${dp.summary.year}`.toLowerCase()
                if (toSearch.search(pattern) !== -1){ dp_new.push(dp); }
            }
        }
        else{
            throw new Error("Unknown searchBy option");
        }
        return {
            datapoints: this.sortDefault(dp_new, false),
            scores: null,
        }
    }

    // sort datapoints by default method, the later added, the first (descending order)
    static sortDefault(datapoints: DataPoint[], reverse = false): DataPoint[]{
        if (reverse){
            return datapoints.sort((a, b) => a.summary.time_added - b.summary.time_added)
        }
        return datapoints.sort((b, a) => a.summary.time_added - b.summary.time_added)
    }

    // return a list of datapoints that are sorted by scores, and sorted scores
    // - reverse: if false, sort in descending order
    static sortByScore<T>(arr: T[], scores: number[], reverse = false): [T[], number[]]{
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
        const ret2 = new Array();
        for (const item of arr_score_sorted){
            ret.push(item[0]);
            ret2.push(item[1]);
        }

        return [ret, ret2];
    }
}