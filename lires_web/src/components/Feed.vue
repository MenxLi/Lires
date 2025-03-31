
<script setup lang="ts">
    import { ref, computed, onMounted } from 'vue';
    import type { FeedDataInfoT } from '../api/protocol';
    import ArticleBlock from './feed/ArticleBlock.vue';
    import { useRouter } from 'vue-router';
    import RefreshIcon from '../assets/icons/refresh.svg'

    import Toolbar from './header/Toolbar.vue';
    import LoadingWidget from './common/LoadingWidget.vue'

    import { lazify } from '../utils/misc';
    import { useConnectionStore } from '@/state/store';

    const conn = useConnectionStore().conn;
    const router = useRouter();

    function todayString(diffDate: number = 0){
        const today = new Date();
        today.setDate(today.getDate() + diffDate);
        return today.toISOString().split('T')[0];
    }

    // search and main data structure
    const fetchCategory = ref("arxiv");
    const fetching = ref(false);
    const allCategories = ref(["arxiv"] as string[])
    const timeBefore = ref(todayString(1));
    const timeAfter = ref(todayString(-1));
    const maxResults = ref(parseInt(router.currentRoute.value.query.maxResults as string) || 100);
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
        conn.featurizeText(searchText.value).then(
            (features) => {
                searchFeature.value = new Float32Array(features);
            },
            () => {
                console.log("failed to featurize");
            },
        )
    }
    const lazyUpdateSearchFeature = lazify(updateSearchFeature, 100);

    if (maxResults.value > 200){
        window.alert("maxResults cannot be larger than 200");
        maxResults.value = 200;
    }
    let initSearchString = router.currentRoute.value.query.search as string || "";
    if (initSearchString !== ""){
        searchText.value = initSearchString;
    }

    const refreshButton = ref(null as HTMLImageElement | null);
    async function runFetchArticles(){
        arxivArticles.value = [];
        const conn = useConnectionStore().conn;
        allCategories.value = ['arxiv'].concat(await conn.getFeedCategories())
        
        fetching.value = true
        const timeBefore_float = new Date(timeBefore.value).getTime() / 1000;
        const timeAfter_float = new Date(timeAfter.value).getTime() / 1000;
        try{
            // const articles = await fetchArticleFromBackend(maxResults.value, fetchCategory.value);
            const articles = await conn.getFeedList(
                {
                    maxResults: maxResults.value, 
                    category: fetchCategory.value, 
                    timeBefore: timeBefore_float, 
                    timeAfter: timeAfter_float
                })
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
        <h1 style="margin-block: 1rem;">
            Daily Feed
            <img ref="refreshButton" :src="RefreshIcon" alt="" class="icon spin" title="refresh the page" @click="(event: MouseEvent)=>{
                const this_ = event.target as HTMLImageElement;
                if (!this_.classList.contains('spin')){
                    this_.classList.add('spin');
                    runFetchArticles().then(()=>this_.classList.remove('spin'))
                }
            }">
        </h1>
        <div id="settings">
            <div style="display: flex; justify-content: center; align-items: center; width: 100%; gap: 0.5rem; flex-flow: row wrap">
                <span>
                    Category: 
                    <select name="category" id="category-select" v-model="fetchCategory" @change="runFetchArticles">
                        <option v-for="category in allCategories" :value="category">{{category}}</option>
                    </select>
                </span>
                <span>
                    Max results: <select v-model="maxResults" @change="runFetchArticles">
                        <option v-for="i in [20, 50, 100, 200, 500]" :value="i">{{i}}</option>
                    </select>
                </span>
                <span>
                    From: <input type="date" v-model="timeAfter" @change="runFetchArticles">
                </span>
                <span>
                    To: <input type="date" v-model="timeBefore" @change="runFetchArticles">
                </span>
            </div>
            <div style="display: flex; justify-content: center; align-items: center; width: 100%; gap: 0.5rem">
                <input type="text" placeholder="Search" @input="lazyUpdateSearchFeature" v-model="searchText" autocomplete="off">
            </div>
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
        flex-direction: column;
        justify-content: center;
        align-items: center;
        gap: 0.5rem;
    }
    div#settings input, div#settings select{
        height: 1.5rem;
        border-radius: 0.5rem;
        padding-inline: 1rem;
        background-color: var(--color-background-soft);
        border: none;
        color: var(--color-text);
    }
    div#settings select{
        min-width: 2rem;
        max-width: 8rem;
        font-weight: bold;
    }
    div#settings input[type="text"]{
        height: 2rem;
        border-radius: 1rem;
        width: 100%;
        margin-block: 0.5rem;
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