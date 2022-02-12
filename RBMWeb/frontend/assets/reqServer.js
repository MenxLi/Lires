//import {SERVER_ADDR, SERVER_PORT} from "./config.js"
import {DataBase} from "./databse.js"

//https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/responseType

const SERVER_ADDR = localStorage.getItem("RBMServerAddr")
const SERVER_PORT = localStorage.getItem("RBMServerPort")

function reqFileList(tags, callbacks){
    let queryKey;
    if (Array.prototype.isPrototypeOf(tags) && tags.length === 0){
        queryKey = "%";
    }
    else {
        queryKey = tags.join("&&");
    }
    const xhr = new XMLHttpRequest();
    const reqStr =  `http://${SERVER_ADDR}:${SERVER_PORT}/main/${queryKey}`;
    console.log(reqStr)
    xhr.open("GET", reqStr, true);
    xhr.responseType = "json"
    xhr.onreadystatechange = function(){
        if (this.readyState == 4){
            if (this.status == 200){
                var db = new DataBase(xhr.response["data"])
                window.database = db
                for (const callback of callbacks){
                    callback();
                }
            }
        }
    }
    xhr.send();
    return
}

function reqPDFFile(uuid){
}

export {reqFileList, reqPDFFile}