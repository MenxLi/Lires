import { DataBase } from "./databse.js"
import {SERVER_ADDR, SERVER_PORT} from "./config.js"


function initTags (){
    const db = window.database
    const tags_frame = document.querySelector("#tags_frame");
    const tags_table = document.createElement("table");
    tags_table.id = "tags_table";
    tags_frame.appendChild(tags_table);
    
    const all_tags = Array.from(db.getAllTags()).sort();

    for (const tag of all_tags){
        const tr = document.createElement("tr");
        tr.className = "tag_tr";
        const td = document.createElement("td");
        td.className = "tag_td";
        const cb = document.createElement("input")
        cb.type = "checkbox";
        cb.className = "tag_cb";
        cb.value = tag;
        cb.onchange = updateSelector;
        const label = document.createElement("label")
        label.className = "tag_label";
        label.htmlFor = tag
        label.innerHTML = tag

        td.appendChild(cb);
        td.appendChild(label);
        tr.appendChild(td);
        tags_table.appendChild(tr);
    }
    console.log(all_tags);
    console.log(db.getDataByTags([]));
}

function updateSelector(){
    const db = window.database;
    const selectedTags = getAllSelectedTags();
    console.log(selectedTags)
    const dataList = db.getDataByTags(selectedTags);
    showData(dataList)
}

function getAllSelectedTags(){
    const selectedTags = new Array();
    const allCbs = document.querySelectorAll(".tag_cb");
    for (const cb of allCbs){
        if (cb.checked){
            selectedTags.push(cb.value);
        }
    }
    return selectedTags

}

function showData(dataList){
    const selector_frame = document.querySelector("#selector_frame");
    // first, clear selector_frame 
    removeChilds(selector_frame)
    // add valid data into it
    const selector_table = document.createElement("table");
    selector_table.id = "selector_table";
    selector_frame.appendChild(selector_table);
    for (const data of dataList){
        const tr = getDataRowElem(data);
        selector_table.appendChild(tr);
    }
}

function getDataRowElem(data){
    const uuid = data["uuid"];
    const tr = document.createElement("tr");
    tr.id = uuid;
    tr.className = "selector_tr";
    const showIndex = [
        ["file_status", ],
        ["year", ],
        ["author", ],
        ["title", ]
    ];
    for (const item of showIndex){
        const query = item[0];
        const td = document.createElement("td");
        td.className = "data_td" + " " + query;
        if (query == "title"){
            const a = document.createElement("a");
            a.href = `http://${SERVER_ADDR}:${SERVER_PORT}/file/${uuid}`;
            a.innerHTML = data[query];
            a.className = "data_a";
            td.appendChild(a);
        }
        else{
            td.innerHTML = data[query];
        }
        tr.appendChild(td);
    }
    return tr
}

function removeChilds(parent){
    while (parent.lastChild){
        parent.removeChild(parent.lastChild);
    }

}

export {initTags, updateSelector};