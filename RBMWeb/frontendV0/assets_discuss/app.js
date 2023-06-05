import {setFileInfoStr, setFileUrl} from "./reqServer.js"
import {getCookie} from "../libs/cookieUtils.js"
import {SERVER_URL} from "../libs/serverAddr.js"

// const SERVER_ADDR = sessionStorage.getItem("RBMServerAddr")
// const SERVER_PORT = sessionStorage.getItem("RBMServerPort")

function initPage() {
    const queryString = window.location.search;
    const uid = queryString.slice(1, );
    // console.log(uuid);
    const noteFrame = document.querySelector("#note_frame");
    const discuss_frame = document.querySelector("#discuss_frame");
    discuss_frame.src = `${SERVER_URL}/discussions/${uid}`;

    setFileInfoStr(uid, document.querySelector("#doc_info"));
    setFileUrl(uid, document.querySelector("#open_doc"));

    document.querySelector("#usr_name").value = localStorage.getItem("RBM_USR_NAME")

    document.querySelector("#submit_btn").addEventListener("click", submitComment);
    document.querySelector("#tab_note").addEventListener("click", () => {
        clickOnTab("note");
    });
    document.querySelector("#tab_doc").addEventListener("click", () => {
        clickOnTab("doc");
    });
    noteFrame.src = `${SERVER_URL}/comment/${uid}/`;
}

function clickOnTab(tab_name) {
    const queryString = window.location.search;
    const uid = queryString.slice(1, );
    const noteFrame = document.querySelector("#note_frame");
    if (tab_name == "note"){
        noteFrame.src = `${SERVER_URL}/comment/${uid}/`;
    }
    else if (tab_name == "doc"){
        noteFrame.src = document.querySelector("#tab_doc").doc_url; // set by setFileUrl
    }
}

function submitComment() {

    const usr_name = document.querySelector("#usr_name").value;
    localStorage.setItem("RBM_USR_NAME", usr_name)

    if (!usr_name){
        alert("Please enter a name");
        return;
    }
    if (!document.querySelector("#comment_input").value){
        alert("Please enter your comment");
        return;
    }

    const queryString = window.location.search;
    const uid = queryString.slice(1, );
    let xhr = new XMLHttpRequest();
    xhr.open("POST", `${SERVER_URL}/discussion_mod`);

    // Requested by tornado
    // https://stackoverflow.com/a/45429322
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    const data = {
      "cmd": "add",
      "file_uid": uid,
      "usr_name": document.querySelector("#usr_name").value,
      // "key": sessionStorage.getItem("RBM_ENC_KEY"),     // set with libs/auth.js
      "key": getCookie("RBM_ENC_KEY"),     // set with libs/auth.js
      "content": document.querySelector("#comment_input").value,
    };
    xhr.onload = () => {
        if (xhr.status === 403){
            alert("Unauthorized.");
        }
        else if (xhr.status === 200){
            document.querySelector("#discuss_frame").contentWindow.location.reload();
            document.querySelector("#discuss_frame").contentWindow.scrollTo( 0, 999999 );
            document.querySelector("#comment_input").value="";
        }
    }
    const params = new URLSearchParams();
    for (let k in data){
        if (data.hasOwnProperty(k)){
            params.set(k, data[k]);
        }
    }
    const toSend = params.toString();
    xhr.send(toSend);
}


initPage()
