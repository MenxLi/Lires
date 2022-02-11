// File name: app.js
// Author: Li, Mengxun
// Email: mengxunli@whu.edu.cn
// Date created: Feb 11, 2022

import {reqFileList} from "./reqServer.js"
import {initTags, updateSelector} from "./renderer.js"


// change css according to scree size
function setElemSize2Screen(){
    const winHeight = window.innerHeight;
    const panelDivs = document.querySelectorAll("div.panel");
    for (const div of panelDivs){
        console.log(div)
        div.style.height = String(parseInt(winHeight*0.8)) + "px";
    }
}

window.addEventListener("resize", (ev) => setElemSize2Screen())


setElemSize2Screen()
reqFileList([], [initTags, updateSelector])