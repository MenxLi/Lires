
function onBtnClicked(){
    // Deprecated...
    // const btn = document.querySelector("#btn_server_config");
    const addrInput = document.querySelector("#server_addr");
    const portInput = document.querySelector("#server_port");
    let addr = addrInput.value;
    let port = portInput.value;
    if (port === ""){
        port = "8079";
    }
    if (addr === ""){
        addr = window.location.hostname;
    }
    sessionStorage.setItem("RBMServerAddr", addr)
    sessionStorage.setItem("RBMServerPort", port)
    // const SERVER_PORT = localStorage.getItem("RBMServerPort")
    window.location.href = "main.html"
}

const btn = document.querySelector("#btn_server_config");
btn.addEventListener("click", onBtnClicked)
