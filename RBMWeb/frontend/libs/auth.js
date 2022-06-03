import { sha256 } from "./sha256.js"
import {SERVER_URL} from "./serverAddr.js"

function maybeLogin(){
	const accessToken = sessionStorage.getItem("RBM_ENC_KEY");
    checkToken(accessToken);
}

function askLogin(){
    const key = prompt("Please enter your access token");
    const encKey = sha256(key);
    checkToken(encKey)
}

function checkToken(encKey,
    onSuccess = () => {sessionStorage.setItem("RBM_ENC_KEY", encKey);},
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

