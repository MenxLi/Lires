
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
        features: Float32Array | null,
    }

    const conn = new ServerConn();

    // search and main data structure
    const fetchCategory = ref("cat:cs.CV OR cat:cs.AI OR stat.ML");
    const searchText = ref("");
    const searchFeature = ref(null as null | Float32Array);
    const arxivArticles = ref([] as ArxivArticleWithFeatures[]);
    const sortedArxivArticles = computed(function(){
        const articleShallowCopy = [...arxivArticles.value] as ArxivArticleWithFeatures[];
        return articleShallowCopy.sort((a, b) => {
            if (searchFeature.value === null || !a.features || !b.features ){
                return 0;
            }
            else{
                const feat_a = a.features as Float32Array;
                const feat_b = b.features as Float32Array;
                const feat_search = searchFeature.value as Float32Array;

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
                searchFeature.value = new Float32Array(features);
            },
            () => {
                console.log("failed to featurize");
            },
        )
    }
    const lazyUpdateSearchFeature = lazify(updateSearchFeature, 100);

    const router = useRouter();
    let maxResults = parseInt(router.currentRoute.value.query.maxResults as string) || 100;
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
                    article_with_features.features = ref(null as null | Float32Array);
                    arxivArticles.value.push(article_with_features);

                    conn.featurize(article.abstract).then(
                        // update article features
                        (features) => {
                            article_with_features.features.value = new Float32Array(features);
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
    <div id="banner">
        <Banner ref="banner"></Banner>
    </div>
    <div id="main">
        <h1>Arxiv daily</h1>
        <div id="settings">
            <select name="category" id="category-select" v-model="fetchCategory" @change="runFetchArticles">
                <option value="cat:cs.CV OR cat:cs.AI OR stat.ML">ALL</option>
                <option value="cat:cs.CV">cs.CV</option>
                <option value="cat:cs.AI">cs.AI</option>
                <option value="cat:stat.ML">stat.ML</option>
            </select>
            <input type="text" placeholder="Search" @input="lazyUpdateSearchFeature" v-model="searchText" autocomplete="off">
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
        margin-top: 40px;
        width: calc(min(1200px, 100vw - 20px));
        min-height: calc(100vh - 40px);
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
</style>