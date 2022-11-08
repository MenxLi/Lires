import { ServerConn } from "./serverConn.js";
import { DataInfoT } from "./protocalT.js";
import {removeChilds} from "./libs/uiUtils.js";
import { DataFilter } from "./dataFilter.js";
import {BACKENDURL, FRONTENDURL} from "./config.js";
import { getLogger } from "./libs/logging.js";
import { checkUsrInfo, eraseUsrInfo } from "./login.js";
import { sleep } from "./libs/timeUtils.js";


// Global storages ===========
// the dataInfoList
var g_datalist: DataInfoT[];
// last dataEntry with action shown
var g_prevActEntry: null|DataEntryElement

interface DataEntryElement extends HTMLDivElement{
    dataInfo: DataInfoT
}

function render(dataInfoList: DataInfoT[]){

    // set global var
    g_datalist = dataInfoList;

    initSearch(dataInfoList);
    showData(dataInfoList);
}

function initSearch(dataInfoList: DataInfoT[]){
    const kwSelect: HTMLSelectElement = document.querySelector("select#search_kw")!;
    removeChilds(kwSelect);
    const showKeys = [
        "year", "title", "authors", "uuid"
    ];
    const df = new DataFilter(dataInfoList);

    if (df){
        for (const k of df.getDataKeys()){
            if (showKeys.includes(k)){
                const option = document.createElement("option");
                option.value = k;
                option.innerHTML = k;
                kwSelect.appendChild(option);
            }
            if (df.getDataKeys().includes("title")){
                kwSelect.value = "title";
            }
        }
    }
}

function showData(dataInfoList: DataInfoT[]){
    function showEntryAct(entry: DataEntryElement){
        if (entry.querySelector("div.entryAct")){
            // If already has act entry, skip re-triggering this function
            return;
        }
        // Add elements
        entry.innerHTML += `
        <div class="entryAct gradIn">
        </div>
        `
        const acts: HTMLInputElement[] = new Array()
        const entryFrame = entry.querySelector("div.entryAct")!;
        const actView = document.createElement("input");
        actView.value = "View"
        acts.push(actView);
        const actNote = document.createElement("input");
        actNote.value = "Note"
        acts.push(actNote);
        const actDiscuss = document.createElement("input");
        actDiscuss.value = "Discuss"
        acts.push(actDiscuss);

        for (const act of acts){
            act.type = "button";
            act.classList.add("smoothTrans");
            entryFrame.appendChild(act);
        }

        // Set callbacks for the actions
        function getOpenFileFunction(): () => void{
            const uid = entry.dataInfo.uuid;
            let destURL: string;
            if (entry.dataInfo["has_file"] && entry.dataInfo["file_type"]===".pdf"){
                destURL = `${BACKENDURL}/doc/${uid}`
            }
            else if (entry.dataInfo["has_file"] && entry.dataInfo["file_type"]===".hpack"){
                destURL = `${BACKENDURL}/doc/${uid}//`
            }
            else if (entry.dataInfo.url){
                destURL = entry.dataInfo.url;
            }
            return () => {
                // if (destURL) window.location.href = destURL;
                if (destURL) window.open(destURL, '_blank')?.focus();
            }
        }
        function getOpenNoteFunction(): ()=>void {
            const uid = entry.dataInfo.uuid;
            return () => {
                const dest = `${BACKENDURL}/comment/${uid}/`;
                // Simulate a mouse click:
                // it will somehow omit the last '/'
                // window.location.href = `${BACKENDURL}/comment/${uid}/`;
                //
                // Use this instead
                window.open(dest, '_blank')?.focus();
            }
        }
        function getOpenDiscussionFunction(): ()=>void {
            const uid = entry.dataInfo.uuid;
            return () => {
                alert("Not implemented yet.")
            }
        }
        actView.addEventListener("click", getOpenFileFunction());
        actNote.addEventListener("click", getOpenNoteFunction());
        actDiscuss.addEventListener("click", getOpenDiscussionFunction());

        // May be remove other entry frame
        if (g_prevActEntry != null && g_prevActEntry.classList == entry.classList){
            // compare if prev activated entry is the current one
            // This may be unnecessary because we are not re-triggering this function 
            // by previous condition checking
            getLogger('rbm').debug("Staying in same entry");
        }
        else{
            // Remove previous entry's action frame
            if (g_prevActEntry){
                removeEntryAct(g_prevActEntry);
            }
            // save this as global
            g_prevActEntry = entry;
        }
    }
    function removeEntryAct(entry: HTMLDivElement){
        // remove entry action frame if it exists
        const actFrame = entry.querySelector("div.entryAct");
        if (actFrame){
            entry.removeChild(actFrame);
        }
    }


    const selectorDiv: HTMLDivElement = document.querySelector("div.selector")!;
    // first, clear selector_frame 
    removeChilds(selectorDiv);
    // a counter for animation delay
    let idx = 0;
    // add valid data into it
    for (const dataInfo of dataInfoList){
        idx += 1;
        const dataEntry = <DataEntryElement>document.createElement("div");
        dataEntry.dataInfo = dataInfo;
        dataEntry.classList.add("dataEntry");
        dataEntry.innerHTML = `
        <div class="entryInfo">
            <div class="yearAuthor">
                <label class="year">${dataInfo.year}</label> 
                <label class="author">${dataInfo.author}</label>
            </div>
            <label class="title">${dataInfo.title}</label>
        </div>
        `
        selectorDiv.appendChild(dataEntry);

        // animation property
        const delay = 0.025*idx + Math.random()*0.1;
        dataEntry.classList.add("gradIn2");
        dataEntry.classList.add("smoothTrans");
        dataEntry.classList.add("hoverMaxout103");
        // dataEntry.classList.add("hoverBlueWhite");
        dataEntry.classList.add(dataInfo.uuid);
        dataEntry.style.animationDelay = delay.toString() + "s";


        dataEntry.addEventListener("mouseover", 
                                   (function(){ return () => { showEntryAct(dataEntry); }})()
                                  )
        dataEntry.addEventListener("mouseleave",
                                   (function(){ 
                                       return async () => { 
                                           // to remove act frame when mouse move out of the entry 
                                           // and not entering another entry
                                           // delay execution is used to resolve
                                           // flashing when hoveing betweeing two entries
                                           await sleep(200);
                                           removeEntryAct(dataEntry); 
                                       }
                                   })()
                                  )
    }
}

// temporary for now
function getAllSelectedTags(): string[]{ return [] };

// Will be called on search change and tag select change
function onFilterData() : void{
    const kwSelect: HTMLSelectElement = document.querySelector("select#search_kw")!;
    const searchBar: HTMLInputElement = document.querySelector("input.search_bar")!;
    const selectedTags = getAllSelectedTags();

    let datalist = DataFilter.filterByTag(g_datalist, selectedTags);
    datalist = DataFilter.filterBySearch(datalist, kwSelect.value, searchBar.value);

    showData(datalist);
}


// MAIN

document.querySelector("input.search_bar")?.addEventListener("input", onFilterData);

const searchParams = new URL(window.location.href).searchParams;
const rawTags = searchParams.get("tags");

getLogger("rbm").debug(`Get tags from url: ${rawTags}`);
let tags: string[];
if (rawTags){
    tags = rawTags.split("&&");
}
else{
    tags = [];
}

if (tags.length == 0){
    // require login
    checkUsrInfo();
}

const conn = new ServerConn();
conn.reqFileList(tags).then(
    (lis) => {
        render(lis);
    }
)
