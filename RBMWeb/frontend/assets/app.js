// File name: app.js
// Author: Li, Mengxun
// Email: mengxunli@whu.edu.cn
// Date created: Feb 11, 2022

import {reqFileList, reqReloadDB} from "./reqServer.js"
import {initTags, initSearch, updateSelector} from "./renderer.js"

const host = window.location.hostname;
const port = window.location.port;
localStorage.setItem("RBMServerAddr", host);
localStorage.setItem("RBMServerPort", port);

// change css according to scree size
function setElemSize2Screen(){
    const winHeight = window.innerHeight;
    const panelDivs = document.querySelectorAll("div.panel");
    for (const div of panelDivs){
        div.style.height = String(parseInt(winHeight)-40) + "px";
    }
}

window.addEventListener("resize", (ev) => setElemSize2Screen())
document.querySelector("#refresh_btn").addEventListener("click", reqReloadDB)
document.querySelector("input.search_bar").addEventListener("input", updateSelector)

setElemSize2Screen()

reqFileList([], [initTags, initSearch, updateSelector])
