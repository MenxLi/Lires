import {setFileInfoStr, setFileUrl} from "./reqServer.js"
import {sha256} from "../libs/sha256.js"

const SERVER_ADDR = sessionStorage.getItem("RBMServerAddr")
const SERVER_PORT = sessionStorage.getItem("RBMServerPort")

function initPage() {
    const queryString = window.location.search;
    const uid = queryString.slice(1, );
    // console.log(uuid);
    const noteFrame = document.querySelector("#note_frame");
    noteFrame.src = `http://${SERVER_ADDR}:${SERVER_PORT}/comment/${uid}/`;
    const discuss_frame = document.querySelector("#discuss_frame");
    discuss_frame.src = `http://${SERVER_ADDR}:${SERVER_PORT}/discussions/${uid}`;
    discuss_frame.addEventListener("load", () => discuss_frame.contentWindow.scrollTo( 0, 999999 ));

    document.querySelector("#submit_btn").addEventListener("click", submitComment);

    setFileInfoStr(uid, document.querySelector("#doc_info"));
    setFileUrl(uid, document.querySelector("#open_doc"));

    document.querySelector("#usr_name").value = sessionStorage.getItem("RBM_USR_NAME")
}

function submitComment() {

    const usr_name = document.querySelector("#usr_name").value;
    sessionStorage.setItem("RBM_USR_NAME", usr_name)

    if (!usr_name){
        alert("Please enter a name");
        return;
    }

    const queryString = window.location.search;
    const uid = queryString.slice(1, );
    let xhr = new XMLHttpRequest();
    xhr.open("POST", `http://${SERVER_ADDR}:${SERVER_PORT}/discussion_mod`);

    // Requested by tornado
    // https://stackoverflow.com/a/45429322
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    const data = {
      "cmd": "add",
      "file_uid": uid,
      "usr_name": document.querySelector("#usr_name").value,
      "key": sha256(document.querySelector("#usr_key").value),
      "content": document.querySelector("#comment_input").value,
    };
    xhr.onload = () => {
        if (xhr.status === 401){
            alert("Unauthorized.");
        }
        else if (xhr.status === 200){
            document.querySelector("#discuss_frame").contentWindow.location.reload();
            // document.querySelector("#discuss_frame").contentWindow.scrollTo( 0, 999999 );
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
