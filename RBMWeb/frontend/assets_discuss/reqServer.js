/*
elem: html element that innerHTML to be changed  
*/
const SERVER_ADDR = localStorage.getItem("RBMServerAddr")
const SERVER_PORT = localStorage.getItem("RBMServerPort")

function setFileInfoStr(uid, elem){
    const queryKey = `${uid}?cmd=stringInfo`
    const reqStr =  `http://${SERVER_ADDR}:${SERVER_PORT}/fileinfo/${queryKey}`;
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
function setFileUrl(uid, elem){
    const queryKey = `${uid}`
    const reqStr =  `http://${SERVER_ADDR}:${SERVER_PORT}/fileinfo/${queryKey}`;
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
                    href = `http://${SERVER_ADDR}:${SERVER_PORT}/doc/${uid}`;
                }
                else if (data["has_file"] && data["file_type"]===".hpack"){
                    href = `http://${SERVER_ADDR}:${SERVER_PORT}/hdoc/${uid}/`;
                }
                else if (data["url"] != ""){
                    href = data["url"];
                }
                else {
                    href = "none";
                }
                elem.onclick = () => {
                    window.open(href);
                }
                console.log(res);
                }
            }
        }
    xhr.send();
}



export {setFileInfoStr, setFileUrl}
