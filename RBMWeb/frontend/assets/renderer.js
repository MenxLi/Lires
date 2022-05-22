
const SERVER_ADDR = localStorage.getItem("RBMServerAddr")
const SERVER_PORT = localStorage.getItem("RBMServerPort")

function initTags (){
    const db = window.database
    const tags_frame = document.querySelector("#tags_frame");
    removeChilds(tags_frame);

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
}

function initSearch(){
    const kwSelect = document.querySelector("select#search_kw");
    removeChilds(kwSelect);
    const showKeys = [
        "year", "title", "authors", "uuid"
    ];
    const db = window.database;
    if (db){
        for (const k of db.getDataKeys()){
            if (showKeys.includes(k)){
                console.log(k);
                const option = document.createElement("option");
                option.value = k;
                option.innerHTML = k;
                kwSelect.appendChild(option);
            }
            if (db.getDataKeys().includes("title")){
                kwSelect.value = "title";
            }
        }
    }
}

function updateSelector(){
    const db = window.database;
    const kwSelect = document.querySelector("select#search_kw");
    const searchBar = document.querySelector("input.search_bar")
    const selectedTags = getAllSelectedTags();
    let dataList = db.getDataByTags(selectedTags);

    dataList = filterDataListBySearch(dataList, kwSelect.value, searchBar.value)
    showData(dataList);
    //renderDataRowsHL();
}

function filterDataListBySearch(datalist, keyword, pattern){
    if (!pattern){
        return datalist;
    }
    const dl_new = new Array();
    for (const d of datalist){
        const value = d[keyword];
        if (value.search(pattern) !== -1){
            dl_new.push(d);
        }
    }
    return dl_new;
}


function getAllSelectedTags(){
    const selectedTags = new Array();
    const allCbs = document.querySelectorAll(".tag_cb");
    for (const cb of allCbs){
        if (cb.checked){
            selectedTags.push(cb.value);
        }
    }
    return selectedTags;
}

function renderDataRowsHL(highligtUUIDs){
    const dataRows = document.querySelectorAll("tr.selector_tr");
    let hlRow;
    for (const dr of dataRows){
        dr.style.backgroundColor = "white";
    }
    if (highligtUUIDs){
        for (const uid of highligtUUIDs){
            console.log(uid)
            hlRow = document.querySelector(`tr#${uid}`);
            hlRow.style.backgroundColor = "#ff0000"
        }
    }
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
        const tr = generateDataRowElem(data);
        selector_table.appendChild(tr);
    }
}

function generateDataRowElem(data){
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
            if (data["has_file"] && data["file_type"]===".pdf"){
                a.href = `http://${SERVER_ADDR}:${SERVER_PORT}/doc/${uuid}`;
            }
            else if (data["has_file"] && data["file_type"]===".hpack"){
                a.href = `http://${SERVER_ADDR}:${SERVER_PORT}/hdoc/${uuid}/`;
            }
            else if (data["url"] != ""){
                a.href = data["url"];
            }
            // a.href = `http://${SERVER_ADDR}:${SERVER_PORT}/file/${uuid}`;
            a.innerHTML = data[query];
            a.className = "data_a";
            td.appendChild(a);
        }
        else{
            td.innerHTML = data[query];
        }
        tr.appendChild(td);
    }
    tr.onclick = dataRowOnClick;
    return tr
}

function dataRowOnClick(){
    const tr = this;
    const uuid = this.id;
    console.log(uuid)
    //renderDataRowsHL([uuid]);
}

function removeChilds(parent){
    while (parent.lastChild){
        parent.removeChild(parent.lastChild);
    }
}

export {initTags, initSearch, updateSelector};
