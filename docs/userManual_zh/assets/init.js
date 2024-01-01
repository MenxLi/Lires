
function backToTop() {
    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}


function initElement() {
    const nav = document.querySelector('#init-nav')
    if (nav){
        nav.innerHTML = `
            <div class="nav-container">
                <a href="./index.html">⬅️ 返回首页</a>
            </div>
        `
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
}

async function replaceKeyword() {
    const startTime = new Date().getTime();
    const keywordURL = {
        "数据卡片": "./datacard.html",
        "扩展数据卡": "./datacard.html",

        "编辑和添加条目": "./add-edit-entry.html",
        "添加条目信息": "./add-edit-entry.html",
        "编辑条目信息": "./add-edit-entry.html",

        "添加和删除文档": "./add-document.html",
        "添加文档": "./add-document.html",
        "删除文档": "./add-document.html",

        "登录页面": "./route.html#sec-login",
        "主界面": "./route.html#sec-main",
        "主页面": "./route.html#sec-main",
        "主页": "./route.html#sec-main",
        "阅读器": "./route.html#sec-reader",
        "仪表盘": "./route.html#sec-dashboard",
        "推送页面": "./route.html#sec-feed",
        "关于页面": "./route.html#sec-about",

        "工具栏": "./toolbar.html",

        "向量搜索": "./filter-entry.html#sec-vector-search",
        "情境搜索": "./filter-entry.html#sec-vector-search",
        "语义搜索": "./filter-entry.html#sec-vector-search",
    }
    // repace keyword with link
    const requiredSections = document.querySelectorAll('.init-keyword')
    for (const keyword of Object.keys(keywordURL)){
        // check if this is the url (without hash and query)
        const __url = window.location.href.split('#')[0].split('?')[0];
        const url = __url.split('/').pop();
        const __aim = keywordURL[keyword].split('#')[0].split('?')[0];
        const aim = __aim.split('/').pop();
        if (url === aim){
            continue;
        }

        // make an async break, so that the page can be rendered first?
        await new Promise((resolve)=>{
            setTimeout(()=>{
                resolve();
            }, 0)
        })

        requiredSections.forEach((item)=>{
            const candidateInnerHtml = item.innerHTML;
            // console.log(keyword, candidateInnerHtml, candidateInnerHtml.indexOf(keyword))
            if (!candidateInnerHtml.includes(keyword)){
                return;
            }

            // check if keyword is in already part of a link
            // const keywordPos = candidateInnerHtml.indexOf(keyword);
            // if (candidateInnerHtml.slice(keywordPos-'class="keyword">'.length, keywordPos) === 'class="keyword">')
            //     { return; }
            // if (candidateInnerHtml.slice(keywordPos+keyword.length, keywordPos+keyword.length+4) === '</a>')
            //     { return; }

            // replace keyword with link
            const newInnerHtml = candidateInnerHtml.replaceAll(
                keyword,
                `<a href="${keywordURL[keyword]}" class="keyword">${keyword}</a>`
            )
            item.innerHTML = newInnerHtml;
        })
    }
    console.log("Time for keyword replacement: ", new Date().getTime()-startTime, "ms")
}

function formatImage(){
    const images = document.querySelectorAll('img');
    for (const image of images){
        image.style.maxWidth = "100%";
    }
}

window.onload = ()=>{
    initElement();
    replaceKeyword();
    formatImage();
}