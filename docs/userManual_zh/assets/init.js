
const nav = document.querySelector('#init-nav')
if (nav){
    nav.innerHTML = `
        <div class="nav-container">
            <a href="./index.html">返回首页</a>
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
    footer.innerHTML = `
        <div class="footer-container">
            ${
            document.querySelector("body").clientHeight > window.innerHeight ?
            '<a onclick="backToTop()" style="cursor: pointer;">返回顶部</a>': ''
            }
            <p>&copy; 2023 <a href="https://github.com/menxli">李梦寻</a></p>
        </div>
    `
}