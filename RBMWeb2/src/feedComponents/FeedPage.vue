
<script setup lang="ts">
    import { ref } from 'vue';
    import { fetchArxivFeed } from './arxivUtils.ts';
    import type { ArxivArticle } from './arxivUtils.ts';

    import { ServerConn } from '../core/serverConn';
    import { getCookie } from '../libs/cookie';
    import { FRONTENDURL } from '../config';
    import Banner from '../components/Banner.vue';
    import type { SearchStatus } from '../components/_interface.ts';

    import ArticleBlock from './ArticleBlock.vue';

    // authentication
    const conn = new ServerConn();
    conn.authUsr(getCookie("encKey") as string).then(
        ()=>{},
        function(){
            const loginSearchParams = new URLSearchParams();
            loginSearchParams.append("from", window.location.href);
            window.location.href = `${FRONTENDURL}/login.html?${loginSearchParams.toString()}`
        },
    )

    // props and data
    const arxivArticles = ref([] as ArxivArticle[]);

    function onSearchChanged(s: SearchStatus){
        // todo: implement
        console.log(s);
        window.alert("Not implemented yet.")
    }

    fetchArxivFeed( 50 , "cat:cs.CV").then(
        (articles) => {
            arxivArticles.value = articles;
        },
    )
</script>

<template>
    <div id="main">
        <Banner @onSearchChange="onSearchChanged"></Banner>
        <h1>Arxiv daily</h1>
        <h2 v-if="arxivArticles.length===0">Fetching...</h2>
        <ArticleBlock v-for="article in arxivArticles" :article="article"></ArticleBlock>
    </div>
</template>

<style scoped>
    #main{
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }
</style>