
<script setup lang="ts">
    import { ref, computed, onMounted } from 'vue';
    import type { FeedDataInfoT } from '../api/protocol';
    import ArticleBlock from './feed/ArticleBlock.vue';
    import { useRouter } from 'vue-router';
    import RefreshIcon from '../assets/icons/refresh.svg'

    import Toolbar from './header/Toolbar.vue';
    import LoadingWidget from './common/LoadingWidget.vue'

    import { lazify } from '../utils/misc';
    import { useConnectionStore } from './store';

    const conn = useConnectionStore().conn;

    // search and main data structure
    const fetchCategory = ref("arxiv");
    const fetching = ref(false);
    const searchText = ref("");
    const searchFeature = ref(null as null | Float32Array);
    const arxivArticles = ref([] as FeedDataInfoT[]);
    const sortedArxivArticles = computed(function(){
        const articleShallowCopy = [...arxivArticles.value];
        return articleShallowCopy.sort((a, b) => {
            if (searchFeature.value === null || !a.feature || !b.feature ){
                return 0;
            }
            else{
                const feat_a = new Float32Array(a.feature);
                const feat_b = new Float32Array(b.feature);
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
        conn.featurize(searchText.value).then(
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

    const refreshButton = ref(null as HTMLImageElement | null);
    async function runFetchArticles(){
        arxivArticles.value = [];

        async function fetchArticleFromBackend(
            maxResults: number,
            category: string,
        ): Promise<FeedDataInfoT[]> {
            const conn = useConnectionStore().conn;
            return await conn.fetchFeedList(maxResults, category)
        }

        fetching.value = true
        try{
            const articles = await fetchArticleFromBackend(maxResults, fetchCategory.value);
            arxivArticles.value = articles;
            updateSearchFeature();
        }
        finally{
            fetching.value = false;
        }
    }

    // MAIN: fetch arxiv feed
    onMounted(() => {
        runFetchArticles().then(
            ()=>refreshButton.value!.classList.remove('spin'),
            ()=>{
                refreshButton.value!.classList.remove('spin');
                window.alert("Failed to fetch articles");
            },
        )
    })
</script>

<template>
    <div id="toolbar">
        <Toolbar ref="toolbar"></Toolbar>
    </div>
    <div id="main">
        <h1>
            Arxiv daily
            <img ref="refreshButton" :src="RefreshIcon" alt="" class="icon spin" title="refresh the page" @click="(event: MouseEvent)=>{
                const this_ = event.target as HTMLImageElement;
                if (!this_.classList.contains('spin')){
                    this_.classList.add('spin');
                    runFetchArticles().then(()=>this_.classList.remove('spin'))
                }
            }">
        </h1>
        <div id="settings">
            <select name="category" id="category-select" v-model="fetchCategory" @change="runFetchArticles">
                <option value="arxiv">ALL</option>
                <option value="arxiv->cs.CV">cs.CV</option>
                <option value="arxiv->cs.AI">cs.AI</option>
                <option value="arxiv->stat.ML">stat.ML</option>
            </select>
            <input type="text" placeholder="Search" @input="lazyUpdateSearchFeature" v-model="searchText" autocomplete="off">
        </div>
        <div id="loadingPlaceholder" v-if="sortedArxivArticles.length===0 && fetching">
            <b>Fetching...</b>
            <LoadingWidget></LoadingWidget>
        </div>
        <div id="loadingPlaceholder" v-if="sortedArxivArticles.length===0 && !fetching">
            <b>No articles found</b>
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

    h1{
        font-weight: bold;
    }
    img.icon {
        height: 20px;
        filter: invert(0.5) opacity(0.35) drop-shadow(0 0 0 var(--color-border)) ;
        transition: all 0.2s;
        cursor: pointer;
    }
    img.icon.spin{
        animation: spin 1s linear infinite;
    }
    img.icon:hover{
        filter: invert(0.5) opacity(0.75) drop-shadow(0 0 0 var(--color-theme)) ;
    }
</style>