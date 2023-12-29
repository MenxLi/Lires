
const nav = document.querySelector('#init-nav')
if (nav){
    nav.innerHTML = `
        <div class="nav-container">
            <a href="./index.html">⬅️ 返回首页</a>
        </div>
    `
}

function backToTop() {
    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}

const footer = document.querySelector('#init-footer')
if (footer){
    const __thisFileName = window.location.pathname.split('/').pop()
    const __thisFileURL = `https://github.com/MenxLi/Lires/blob/dev/docs/userManual_zh/${__thisFileName}`
    footer.innerHTML = `
        <hr>
        <div class="footer-container">
            <p>
                <a href="${__thisFileURL}">编辑此页</a>
                ${
                document.querySelector("body").clientHeight > window.innerHeight ?
                ' | <a onclick="backToTop()" style="cursor: pointer;">返回顶部</a>': ''
                }
                <br>
                &copy; 2023 李梦寻
            </p>
        </div>
    `
}