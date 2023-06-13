
<script setup lang="ts">
    import { ref, computed} from 'vue';
    import { fetchArxivFeed } from './arxivUtils.ts';
    import { ArxivArticleWithFeatures } from './arxivUtils.ts';

    import { ServerConn } from '../core/serverConn';
    import { getCookie } from '../libs/cookie';
    import { FRONTENDURL } from '../config';
    import Banner from '../components/Banner.vue';

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
    const searchText = ref("");
    const searchFeature = ref(null as null | number[]);
    const arxivArticles = ref([] as ArxivArticleWithFeatures[]);
    const sortedArxivArticles = computed(function(){
        const articleShallowCopy = [...arxivArticles.value];
        return articleShallowCopy.sort((a, b) => {
            if (searchFeature.value === null || !a.features || !b.features ){
                return 0;
            }
            else{
                const feat_a = a.features as number[];
                const feat_b = b.features as number[];
                const feat_search = searchFeature.value as number[];

                // calculate which vector is closer to the search vector
                const dist_a = feat_a.reduce((acc, cur, idx) => {
                    return acc + (cur - feat_search[idx]) ** 2;
                }, 0);
                const dist_b = feat_b.reduce((acc, cur, idx) => {
                    return acc + (cur - feat_search[idx]) ** 2;
                }, 0);
                return dist_a - dist_b;
            }
        })
    })


    function onSearchChanged(){
        // update searchFeature
        if (searchText.value.trim() === ""){
            searchFeature.value = null;
            return
        }
        new ServerConn().featurize(searchText.value).then(
            (features) => {
                searchFeature.value = features;
            },
            () => {
                console.log("failed to featurize");
            },
        )
    }

    // MAIN: fetch arxiv feed
    const urlSearchParams = new URLSearchParams(window.location.search);    // get maxResults from url
    let maxResults = parseInt(urlSearchParams.get("maxResults") as string) || 25;
    if (maxResults > 100){ maxResults = 100; }
    let initSearchString = urlSearchParams.get("search") as string || "";
    if (initSearchString !== ""){
        searchText.value = initSearchString;
        onSearchChanged();
    }
    fetchArxivFeed( maxResults , "cat:cs.CV").then(
        (articles) => {
            for (const article of articles){
                const article_with_features = article as ArxivArticleWithFeatures;
                article_with_features.features = null;
                arxivArticles.value.push(article_with_features);
                conn.featurize(article.abstract).then(
                    (features) => {
                        article_with_features.features = features;
                    },
                    () => {
                        console.log("failed to featurize: ", article.id);
                    },
                )
            }
        },
    )
</script>

<template>
    <div id="main">
        <Banner :showSearch="false"></Banner>
        <h1>Arxiv daily</h1>
        <input type="text" placeholder="Search" @input="onSearchChanged" v-model="searchText">
        <h2 v-if="sortedArxivArticles.length===0">Fetching...</h2>
        <ArticleBlock v-for="article in sortedArxivArticles" :article="article"></ArticleBlock>
    </div>
</template>

<style scoped>
    #main{
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }
</style>