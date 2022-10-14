import { ServerConn } from "./serverConn.js";
import { DataInfoT } from "./protocalT.js";
import {removeChilds} from "./libs/uiUtils.js";
import { DataFilter } from "./dataFilter.js";
import {BACKENDURL, FRONTENDURL} from "./config.js";
import { getLogger } from "./libs/logging.js";
import { checkUsrInfo, eraseUsrInfo } from "./login.js";


// Global storage of the dataInfoList
var g_datalist: DataInfoT[];

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
    const selectorDiv: HTMLDivElement = document.querySelector("div.selector")!;
    // first, clear selector_frame 
    removeChilds(selectorDiv);
    // a counter for animation delay
    let idx = 0;
    // add valid data into it
    for (const dataInfo of dataInfoList){
        idx += 1;
        const dataEntry = document.createElement("div");
        dataEntry.classList.add("dataEntry");
        dataEntry.innerHTML = `
        <div class="yearAuthor">
            <label class="year">${dataInfo.year}</label> 
            <label class="author">${dataInfo.author}</label>
        </div>
        <label class="title">${dataInfo.title}</label>
        `
        selectorDiv.appendChild(dataEntry);

        // animation property
        const delay = 0.05*idx + Math.random()*0.1;
        dataEntry.classList.add("gradIn2");
        dataEntry.classList.add("smoothTrans");
        dataEntry.classList.add("hoverMaxout105");
        dataEntry.classList.add("hoverBlueWhite");
        dataEntry.style.animationDelay = delay.toString() + "s";

        // on click
        function getOnClickFunction(): () => void{
            const uid = dataInfo.uuid;
            let destURL: string;
            if (dataInfo["has_file"] && dataInfo["file_type"]===".pdf"){
                destURL = `${BACKENDURL}/doc/${uid}`
            }
            else if (dataInfo["has_file"] && dataInfo["file_type"]===".hpack"){
                destURL = `${BACKENDURL}/doc/${uid}`
            }
            return () => {
                if (destURL) window.location.href = destURL;
            }
        }

        dataEntry.addEventListener("click", getOnClickFunction());
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
