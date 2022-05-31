import {setFileInfoStr, setFileUrl} from "./reqServer.js"

const SERVER_ADDR = localStorage.getItem("RBMServerAddr")
const SERVER_PORT = localStorage.getItem("RBMServerPort")

function initPage() {
    const queryString = window.location.search;
    const uid = queryString.slice(1, );
    // console.log(uuid);
    const noteFrame = document.querySelector("#note_frame");
    noteFrame.src = `http://${SERVER_ADDR}:${SERVER_PORT}/comment/${uid}/`;


    let queryKey, reqStr
    // Change file

    setFileInfoStr(uid, document.querySelector("p#doc_info"))


    // onclick open document button
    setFileUrl(uid, document.querySelector("input#open_doc"))
}

function openDoc() {
    console.log("open")
}

initPage()
