import { sha256 } from "./sha256.js"
import {SERVER_URL} from "./serverAddr.js"
import {getCookie, setCookie} from "./cookieUtils.js"

function maybeLogin(){
	// const accessToken = sessionStorage.getItem("RBM_ENC_KEY");
	const accessToken = getCookie("RBM_ENC_KEY");
    checkToken(accessToken);
}

function askLogin(){
    let key;
    do{
        key = prompt("Please enter your access token");
    }while(!key);
    const encKey = sha256(key);
    checkToken(encKey)
}

function checkToken(encKey,
    // onSuccess = () => {sessionStorage.setItem("RBM_ENC_KEY", encKey)},
    onSuccess = () => {setCookie("RBM_ENC_KEY", encKey, 2)},
    onFailure = askLogin,
    onError = ()=>{alert("error"); askLogin()}
){
	const xhr = new XMLHttpRequest();
    xhr.open("POST", `${SERVER_URL}/auth`, false);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    
    xhr.onload = () => {
        if (xhr.status === 200){
            onSuccess();
        }
        else if (xhr.status == 401){
            onFailure();
        }
        else {
            onError();
        }
    }
    const params = new URLSearchParams();
    params.set("key", encKey);
    xhr.send(params.toString());
}

maybeLogin()

