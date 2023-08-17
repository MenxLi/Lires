
<script setup lang="ts">
    import { ref, computed, onMounted } from 'vue';
    import { fetchArxivFeed } from './feed/arxivUtils.ts';
    import { ArxivArticle } from './feed/arxivUtils.ts';
    import ArticleBlock from './feed/ArticleBlock.vue';
    import { useRouter } from 'vue-router';

    import Banner from './common/Banner.vue';
    import LoadingWidget from './common/LoadingWidget.vue'

    import { ServerConn } from '../core/serverConn';
    import { lazify } from '../libs/misc';


    export interface ArxivArticleWithFeatures extends ArxivArticle{
        features: number[] | null,
    }

    const conn = new ServerConn();

    // search and main data structure
    const fetchCategory = ref("cat:cs.CV");
    const searchText = ref("");
    const searchFeature = ref(null as null | number[]);
    const arxivArticles = ref([] as ArxivArticleWithFeatures[]);
    const sortedArxivArticles = computed(function(){
        const articleShallowCopy = [...arxivArticles.value] as ArxivArticleWithFeatures[];
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


    function updateSearchFeature(){
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
    const lazyUpdateSearchFeature = lazify(updateSearchFeature, 200);

    const router = useRouter();
    let maxResults = parseInt(router.currentRoute.value.query.maxResults as string) || 50;
    if (maxResults > 200){
        window.alert("maxResults cannot be larger than 200");
        maxResults = 200;
    }
    let initSearchString = router.currentRoute.value.query.search as string || "";
    if (initSearchString !== ""){
        searchText.value = initSearchString;
    }

    function runFetchArticles(){
        arxivArticles.value = [];
        fetchArxivFeed(
            maxResults , 
            fetchCategory.value, 
            ).then(
            (articles) => {
                for (const article of articles){
                    const article_with_features = article as any;       // type: ArticleWithFeatures
                    article_with_features.features = ref(null as null | number[]);
                    arxivArticles.value.push(article_with_features);

                    conn.featurize(article.abstract).then(
                        // update article features
                        (features) => {
                            article_with_features.features.value = features;
                        },
                        () => {
                            console.log("failed to featurize: ", article.id);
                        },
                    )
                }
            },
        )
        updateSearchFeature();
    }

    // MAIN: fetch arxiv feed
    onMounted(() => {
        runFetchArticles();
    })
</script>

<template>
    <div id="main">
        <div id="banner">
            <Banner ref="banner"></Banner>
        </div>
        <h1>Arxiv daily</h1>
        <div id="settings">
            <select name="category" id="category-select" v-model="fetchCategory" @change="runFetchArticles">
                <option value="cat:cs.CV">cs.CV</option>
                <option value="cat:cs.AI">cs.AI</option>
            </select>
            <input type="text" placeholder="Search" @input="lazyUpdateSearchFeature" v-model="searchText">
        </div>
        <div id="loadingPlaceholder" v-if="sortedArxivArticles.length===0">
            <b>Fetching...</b>
            <LoadingWidget></LoadingWidget>
        </div>
        <ArticleBlock v-for="article in sortedArxivArticles" :article="article"></ArticleBlock>
    </div>
</template>

<style scoped>
    #main{
        width: calc(min(1200px, 100vw - 30px));
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }
    div#loadingPlaceholder{
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        flex-grow: 1;
    }
    div#settings{
        display: flex;
        flex-direction: row;
        justify-content:center;
        align-items: center;
    }

    div#banner{
        width: 100%;
        padding-top: 10px;
    }
</style>