import { FRONTENDURL } from "./config.js";
import { setCookie, getCookie } from "./libs/cookie.js";
import { sha256 } from "./libs/sha256lib.js";
import {ServerConn} from "./serverConn.js"

const STAY_LOGIN_DAYS = 3;

function encTextSha256(txt: string): string{
    const enc = sha256(txt);
    if (enc){
        return enc
    }
    else{
        throw new Error("Error on encoding sha256: check if you input non-ascii code...")
    }
}

function onSubmitLogin(){
    const conn = new ServerConn();
    const keyInput: HTMLInputElement = document.querySelector("#key_input")!;
    const usrKey: string = keyInput.value;
    const encKey = encTextSha256(usrKey);

    const keepLoginCheckbox: HTMLInputElement = document.querySelector("#stay_login_chk")!;
    let keepTime: null|number = STAY_LOGIN_DAYS;
    conn.authUsr(encKey, {
        onSuccess : () => {
            if (!keepLoginCheckbox.checked){
                keepTime = null;
            }
            setCookie("usrEncKey", encKey, keepTime);
            setCookie("keepLogin", keepLoginCheckbox.checked?"1":"0", keepTime);
            window.location.href = `${FRONTENDURL}/index.html`;
        },
        onFailure : (msg: string) => {
            alert(msg);
        }
    });
}

export function eraseUsrInfo(){
    setCookie("usrEncKey", "", -1);
}

export function checkUsrInfo(): void {
    const conn = new ServerConn();
    const usrEncKey = getCookie("usrEncKey");
    const keepLogin: boolean = Number.parseInt(getCookie("keepLogin")) == 1? true:false;
    let keepTime: null |number = null;
    if (keepLogin){
        keepTime = STAY_LOGIN_DAYS;
    }
    conn.authUsr(usrEncKey, {
        onSuccess : () => {
            setCookie("usrEncKey", usrEncKey, keepTime);
        },
        onFailure : (msg: string) => {
            window.location.href = `${FRONTENDURL}/login.html`;
        }
    });
}

// main
// this script may be impoted as a module
// but the following code won't run on other scripts
// because querySelector will result in null
const submitBtn = document.querySelector("#submit_login_btn");
if (submitBtn){
    submitBtn.addEventListener("click", onSubmitLogin);
}
