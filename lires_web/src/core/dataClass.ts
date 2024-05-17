import type { DataInfoT } from "../api/protocol";
import type { ServerConn } from "../api/serverConn";
import {useDataStore, useSettingsStore } from "@/state/store";
import { DataTags } from "./tag";

import { Mutex } from "async-mutex";

export class DataPoint {
    summary: DataInfoT;
    supp: Record<'note' | 'abstract', string | null>;
    conn: ServerConn;

    constructor(conn: ServerConn, summary: DataInfoT) {
        this.summary = summary;
        // supplimentary information for this datapoint,
        // need to fetch from server
        // it is designed to be a lazy fetch to save bandwidth
        this.supp = {
            note: null,
            abstract: null,
        }
        this.conn = conn;
    }

    get backendUrl(): string{ return this.conn.baseURL; }

    get dtype(): string{ return this.summary.doc_type; }
    get tags(): DataTags{ return new DataTags(this.summary.tags); }
    get uid(): string{ return this.summary.uuid; }
    get title(): string{ return this.summary.title; }
    get authors(): string[] { return this.summary.authors; }
    get year(): string{ return this.summary.year; }
    get publication(): string | null{ return this.summary.publication; }
    get url(): string | null{ return this.summary.url; }
    get bibtex(): string{ return this.summary.bibtex; }
    // get docSize(): number{ return this.summary.doc_size; }
    // get noteLinecount(): number{ return this.summary.note_linecount; }
    // get hasAbstract(): boolean{ return this.summary.has_abstract; }
    // get hasFile(): boolean{ return this.summary.has_file; }
    // get fileType(): string{ return this.summary.file_type; }
    // get timeAdded(): number{ return this.summary.time_added; }
    // get timeModified(): number{ return this.summary.time_modified; }

    toString(){
        return `${this.summary.title} - ${this.authorAbbr()} (${this.summary.year}) [uid: ${this.summary.uuid}]`
    }

    // will update this.supp.abstract
    fetchAbstract(): Promise<string> {
        return new Promise((resolve, reject) => {
            this.conn.reqDatapointAbstract(this.summary.uuid).then((data) => {
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
            this.conn.updateDatapointAbstract(this.summary.uuid, abstract).then((data) => {
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
            this.conn.reqDatapointNote(this.summary.uuid).then((data) => {
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
        // note = note.replace(new RegExp(`${this.backendUrl}/misc/${this.summary.uuid}\\?fname=`, 'g'), './misc/');
        return new Promise((resolve, reject) => {
            this.conn.updateDatapointNote(
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

    deleteMiscFile(fname: string): Promise<boolean>{ return this.conn.deleteMiscFile(this.summary.uuid, fname); }
    renameMiscFile(fname: string, newname: string): Promise<boolean>{ return this.conn.renameMiscFile(this.summary.uuid, fname, newname); }
    listMiscFiles(): Promise<Record<'fname'|'rpath'|'url', string>[]>{ 
        const fnameList = this.conn.reqMiscFileList(this.summary.uuid); 
        const urlBase = `${this.backendUrl}/misc/${this.summary.uuid}`;
        return fnameList.then((data) => {
            return data.map((fname) => {
                const sparam = new URLSearchParams();
                sparam.append("fname", fname);
                sparam.append("_u", useDataStore().user.id.toString());
                return {
                    fname: fname,
                    rpath: `./misc/${fname}`,
                    url: `${urlBase.toString()}?${sparam.toString()}`,
                }
            })
        })
    }
    // return a list of raw image urls
    uploadMisc(files: File[]): Promise<string[]>{
        return new Promise((resolve, reject) => {
            this.conn.uploadMiscFiles(this.summary.uuid, files).then(
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
        return this.conn.uploadDocument(this.summary.uuid, doc);
    }
    freeDocument(): Promise<DataInfoT>{
        return this.conn.deleteDocument(this.summary.uuid);
    }

    update(summary: null | DataInfoT = null): Promise<DataInfoT> {
        if (summary !== null) {
            this.summary = summary;
            return Promise.resolve(summary);
        }

        const res = this.conn.reqDatapointSummary(this.summary.uuid);
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
            return `${this.backendUrl}/doc/${uid}?_u=${useDataStore().user.id}`;
        }
        if (!this.summary["has_file"] && this.url){
            return this.url;
        }
        return "about:blank";
    }

    // will wrap the url with backend pdfjs viewer if the url is a pdf
    getOpenDocURL({
        extraPDFViewerParams = {} as Record<string, string>,
        urlHashMark = "" as string,
    } = {}): string {
        const backendPdfjsviewer = `${this.backendUrl}/pdfjs/web/viewer.html`;
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

    fileType(): "" | "html" | "pdf" | "url" | "unknown" {
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
    doc_type: "",
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
    private cache: Record<string, DataPoint>;
    private tags: DataTags;
    private uids: string[];
    private dataInfoAcquireMutex = new Mutex();

    conn: ServerConn;
    _initliazed: boolean;

    constructor(conn: ServerConn){
        // TODO: handle changes of the database from other clients
        this.cache = {}                         // a cache of all fetched data points
        this.uids = new Array();                // a set of all uids, fetched from server
        this.tags = new DataTags();             // all tags of the database, fetched from server
        this._initliazed = false;

        this.conn = conn;
    }

    get initialized(): boolean{
        return this._initliazed;
    }

    async init(){
        await this.updateKeyCache();
        await this.updateTagCache();
        this._initliazed = true;
        console.log("Get init data of size: ", 
            (
                (JSON.stringify(this.uids) + JSON.stringify(this.tags)).length
                 * 2 / 1024 / 1024
            ).toPrecision(2), "MB");
    }
    allTags() : DataTags { return this.tags; }
    allKeys() : string[] { return this.uids; }
    async updateKeyCache(){ this.uids = await this.conn.reqAllKeys(); }
    async updateTagCache(){ this.tags = new DataTags(await this.conn.reqAllTags()); }

    async update(summary: DataInfoT, syncTags = true): Promise<DataPoint> {
        let oldTagsOfUpdatedData;
        if (summary.uuid in this.cache){
            this.cache[summary.uuid].update(summary);
            oldTagsOfUpdatedData = this.cache[summary.uuid].tags;
        }else{
            this.cache[summary.uuid] = new DataPoint(this.conn, summary);
            oldTagsOfUpdatedData = new DataTags();
        }

        if (!this.uids.includes(summary.uuid)){
            // add to start of the list
            this.uids.unshift(summary.uuid);
        }

        // maybe the updated data has new tags, or some of the old tags are not used anymore
        // in this case, the tag cache should be updated
        const shouldUpdateTagCache = (oldTagsOfUpdatedData: DataTags) => {
            const currentTagPool = new DataTags();
            for (const uid in this.cache){
                currentTagPool.union_(this.cache[uid].tags);
            }
            // new tags maybe introduced by the updated data
            // update the tag cache directly, without request to server
            this.tags.union_(currentTagPool);
            // if the old tags of the updated data is not a subset of the current tag pool
            // then the tag cache should be updated
            return !oldTagsOfUpdatedData.issubset(currentTagPool)
        }
        // check if the tag cache should be updated
        if (syncTags && shouldUpdateTagCache(oldTagsOfUpdatedData)){
            await this.updateTagCache();
        }
        return this.cache[summary.uuid];
    }

    clear(){
        this.cache = {}                         // a cache of all fetched data points
        this.uids = new Array();                // a set of all uids, fetched from server
        this.tags = new DataTags([]);           // all tags of the database, fetched from server
        this._initliazed = false;
    }

    async delete(uuid: string, syncTags = true){
        let oldTagsOfDeletedData: DataTags | null;
        if (uuid in this.cache){
            oldTagsOfDeletedData = this.cache[uuid].tags;
            delete this.cache[uuid];
        }
        else{
            oldTagsOfDeletedData = null;
        }

        if (this.uids.includes(uuid)){
            this.uids = this.uids.filter((uid) => uid !== uuid);
        }

        // maybe the deleted data has the only tag in the database
        // in this case, the tag cache should be updated
        const shouldUpdateTagCache = (oldTagsOfDeletedData: DataTags | null) => {
            if (oldTagsOfDeletedData === null){ return true; }
            // collect all tags of the database
            const allTags = new DataTags();
            for (const uid in this.cache){
                allTags.union_(this.cache[uid].tags);
            }
            return !oldTagsOfDeletedData.issubset(allTags)
        }
        if (syncTags && shouldUpdateTagCache(oldTagsOfDeletedData)){
            await this.updateTagCache();
        }
    }

    hasCache(uuid: string): boolean{
        return uuid in this.cache;
    }

    getDummy(): DataPoint{ return new DataPoint(this.conn, _dummyDataSummary); }

    async aget(uid: string): Promise<DataPoint>{
        if (!(uid in this.cache)){
            try{
                const dpInfo = await this.conn.reqDatapointSummary(uid);
                this.cache[uid] = new DataPoint(this.conn, dpInfo);
            }
            catch(err){
                console.warn("Caught error in aget: ", err);
                return new DataPoint(this.conn, _dummyDataSummary);
            }
        }
        return this.cache[uid];
    }

    async agetMany(uuids: string[], strict_exist = true, fallback = true): Promise<DataPoint[]>{

        const _getWithSingleRequest = async ()=>{
            this.dataInfoAcquireMutex.acquire();
            try{
                // optimize for the case where all uuids are surely exist in the database
                const cachedIds = Object.keys(this.cache);
                const notCached = uuids.filter((uid) => !cachedIds.includes(uid));
                if (notCached.length === 0){
                    return uuids.map((uid) => this.cache[uid]);
                }
                // done with a single request, this is faster but require all uids to be exist
                const notCachedSummaries = await this.conn.reqDatapointSummaries(notCached);
                console.log("DEBUG: get data points of size: ", notCachedSummaries.length)
                // assamble the result
                const notCachedDps = notCachedSummaries.map((summary) => new DataPoint(this.conn, summary));
                // save to cache
                notCachedDps.forEach((dp) => {
                    this.cache[dp.uid] = dp;
                })
            }
            catch(err){ throw err; }
            finally{ this.dataInfoAcquireMutex.release(); }

            // return the result
            const datapoints = uuids.map((uid) => this.cache[uid]);
            return datapoints;
        }

        const _getWithParallelRequest = async ()=>{
            // done in parallel, handle the case where some uids are not exist
            const datapoints = await Promise.all(uuids.map((uid) => {
                return this.aget(uid);
            }));
            return datapoints;
        }

        if (strict_exist){
            try{ return await _getWithSingleRequest(); }
            catch(err){
                if (fallback){
                    console.warn("Caught error in agetMany: ", err);
                    return await _getWithParallelRequest();
                }
                else{
                    throw err;
                }
            }
        }
        return await _getWithParallelRequest();
    }

    async agetByAuthor(author: string): Promise<DataPoint[]>{
        const res = await this.conn.query({
            searchBy: "author",
            searchContent: author,
        });
        return await this.agetMany(res.uids);
    }

    getCacheByTags(tags: string[]| DataTags): DataPoint[] {
        tags = new DataTags(tags);
        const valid_data = [];
        for (const uid in this.cache){
            const data = this.cache[uid];
            const data_tag = new DataTags(data.summary["tags"]);
            if (tags.issubset(data_tag.withParents())) {
                valid_data.push(data)
            }
        }
        return valid_data;
    }
}