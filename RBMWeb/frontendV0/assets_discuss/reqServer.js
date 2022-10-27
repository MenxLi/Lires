import {SERVER_URL} from "../libs/serverAddr.js"

// const SERVER_ADDR = sessionStorage.getItem("RBMServerAddr")
// const SERVER_PORT = sessionStorage.getItem("RBMServerPort")

function setFileInfoStr(uid, elem){
    const queryKey = `${uid}?cmd=stringInfo`
    const reqStr =  `${SERVER_URL}/fileinfo/${queryKey}`;
    const xhr = new XMLHttpRequest();
    console.log("sending...", reqStr)
    xhr.open("GET", reqStr, true);
    xhr.responseType = "text"
    xhr.onreadystatechange = function(){
        if (this.readyState == 4){
            if (this.status == 200){
                    const res = xhr.response;
                    elem.innerHTML = res.replaceAll("\n", " <br>");
                }
            }
        }
    xhr.send();
}

/*
elem: html element whose src to be changed  
*/
function setFileUrl(uid, btn_elem){
    const queryKey = `${uid}`
    const reqStr =  `${SERVER_URL}/fileinfo/${queryKey}`;
    const xhr = new XMLHttpRequest();
    console.log("sending...", reqStr)
    xhr.open("GET", reqStr, true);
    xhr.responseType = "json"
    xhr.onreadystatechange = function(){
        if (this.readyState == 4){
            if (this.status == 200){
                const res = xhr.response;
                const data = res;
                let href;
                if (data["has_file"] && data["file_type"]===".pdf"){
                    href = `${SERVER_URL}/doc/${uid}`;
                }
                else if (data["has_file"] && data["file_type"]===".hpack"){
                    href = `${SERVER_URL}/hdoc/${uid}/`;
                }
                else if (data["url"] != ""){
                    href = data["url"];
                }
                else {
                    href = "none";
                }
                btn_elem.onclick = () => {
                    window.open(href);
                }
                document.querySelector("#tab_doc").doc_url = href; // define a entry to tab-doc
                console.log(res);
                }
            }
        }
    xhr.send();
}

export {setFileInfoStr, setFileUrl}