
function onBtnClicked(){
    const btn = document.querySelector("#btn_server_config");
    const addrInput = document.querySelector("#server_addr");
    const portInput = document.querySelector("#server_port");
    const addr = addrInput.value;
    let port = portInput.value;
    if (port === ""){
        port = "8079";
    }
    localStorage.setItem("RBMServerAddr", addr)
    localStorage.setItem("RBMServerPort", port)
    const SERVER_ADDR = localStorage.getItem("RBMServerAddr")
    const SERVER_PORT = localStorage.getItem("RBMServerPort")
    //console.log(SERVER_ADDR);
    //console.log(SERVER_PORT);
    window.location.href = "main.html"
}

const btn = document.querySelector("#btn_server_config");
btn.addEventListener("click", onBtnClicked)