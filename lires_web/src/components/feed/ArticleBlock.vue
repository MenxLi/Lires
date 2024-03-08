
<script setup lang="ts">
    import type { ArxivArticleWithFeatures } from '../Feed.vue';
    import { bibtexFromArxiv } from '../../utils/arxiv';
    import {useConnectionStore, useDataStore } from '../store';
    import { DataPoint } from '../../core/dataClass';
    import FileRowContainer from '../home/FileRowContainer.vue';
    import FloatingWindow from '../common/FloatingWindow.vue';
    import DataEditor from '../home/DataEditor.vue';
    import { computed, ref } from 'vue';
    import { openURLExternal } from '../../utils/misc';
    import { sortByScore } from '../../core/misc';

    const props = defineProps<{
        article: ArxivArticleWithFeatures,
    }>()
    const dataStore = useDataStore();
    const conn = useConnectionStore().conn;

    const dataEditor = ref(null as null | typeof DataEditor);
    async function showDataEditor(){
        dataEditor.value?.show({
            datapoint: null,
            bibtex: bibtexFromArxiv(props.article),
            tags: [],
            url: props.article.link,
        });
    }

    const allAuthorPapers = ref<Record<string, DataPoint[]>>({});
    async function gatherAuthorPapers(){
        const allAuthors = props.article.authors;
        const allPubs = await Promise.all(allAuthors.map((author) => {
            return dataStore.database.agetByAuthor(author);
        }))
        allAuthorPapers.value = {};
        for (let i = 0; i < allAuthors.length; i++){
            allAuthorPapers.value[allAuthors[i]] = allPubs[i];
        }
    }
    gatherAuthorPapers()

    const authorDatabasePublicationCount = computed(()=>{
        // return a map of author to publication count
        const res: Record<string, number | null> = {};
        for (const author in allAuthorPapers.value){
            if (allAuthorPapers.value[author]){
                res[author] = allAuthorPapers.value[author].length;
            }
            else{
                res[author] = null;
            }
        }
        return res;
    })

    const showAuthorPapers = ref(false);
    const authorPapers = ref([] as DataPoint[]);

    function onClickAuthorPubCount(author: string){
        // author = formatAuthorName(author);
        authorPapers.value = allAuthorPapers.value[author];
        if (!authorPapers.value){
            authorPapers.value = [];
        }
        // remove self from authorPapers
        showAuthorPapers.value = true;
    }

    // related articles
    const relatedArticles = ref([] as DataPoint[]);
    const relatedArticlesScores = ref([] as number[]);
    const relatedArticlesScoresByUid = computed(() => {
        const res = {} as {[uid: string]: number|string};
        for (let i = 0; i < relatedArticles.value.length; i++){
            res[relatedArticles.value[i].summary.uuid] = relatedArticlesScores.value[i].toPrecision(4);
        }
        return res;
    })
    function queryRelatedArticles(){
        if (relatedArticles.value.length > 0){
            return;
        }
        conn.search(
            "searchFeature", { pattern: props.article.abstract, n_return: 8 }
            ).then(
                (res) => {
                    const scores = new Array();
                    const uuids = new Array();
                    for (const uid of Object.keys(res)){
                        scores.push(res[uid]?.score);
                        uuids.push(uid);
                    }
                    const sortedDpSc = sortByScore(uuids, scores);
                    dataStore.database.agetMany(sortedDpSc[0]).then((dps)=>{
                        relatedArticles.value = dps;
                        relatedArticlesScores.value = sortedDpSc[1];
                    })
                }
            )
    }

</script>

<template>
    <DataEditor ref="dataEditor"></DataEditor>
    <FloatingWindow v-model:show="showAuthorPapers" title="Publications in the database" @onClose="authorPapers=[]">
        <div id="authorPapers">
            <FileRowContainer :uids=" authorPapers.map((dp)=>dp.summary.uuid) "></FileRowContainer>
        </div>
    </FloatingWindow>
    <div id="feed-main" class="slideInFast">
        <div class="articleBlock">
            <div class="titleBlock">
                <h2>{{ props.article.title }}</h2>
                <label class="titleId">{{ props.article.id }}</label>
            </div>
            <div class="authors">
                <label>[Authors] </label>
                <span v-for="(author, index) in props.article.authors" class="authorSpan">
                    <a @click="()=>openURLExternal(`https://arxiv.org/search/?query=${author}&searchtype=author`)">{{ author }}</a>
                    <a class="pubCount" v-if="authorDatabasePublicationCount[author]" @click="()=>onClickAuthorPubCount(author)">
                        {{ ` (${authorDatabasePublicationCount[author]})` }}
                    </a>
                    <span v-if="index < props.article.authors.length - 1">, </span>
                </span>
            </div>
            <div class="actions">
                <a @click="()=>openURLExternal(`https://arxiv.org/abs/${article.id}`)">Arxiv</a> |
                <a @click="()=>openURLExternal(`https://arxiv.org/pdf/${article.id}.pdf`)">PDF</a> |
                <a @click="showDataEditor">Collect</a>
            </div>
            <p>Published: {{ props.article.publishedTime }}</p>
            <details>
                <summary>Abstract</summary>
                <p>{{ props.article.abstract }}</p>
            </details>
            <details>
                <summary @click="queryRelatedArticles">Related articles</summary>
                <div id="relatedArticles">
                    <FileRowContainer :uids="
                        relatedArticles.map((dp)=>dp.summary.uuid)
                    ":scores="relatedArticlesScoresByUid"/>
                </div>
            </details>
        </div>
    </div>

    <!-- <div class="sep"></div> -->
</template>

<style scoped>
    #authorPapers{
        width: 100%;
        max-height: 80vh;
        min-width: 360px;
    }
    a:hover{
        cursor: pointer;
    }
    div#tag-selector{
        padding: 5px;
        padding-left: 10px;
        padding-right: 10px;
    }
    div#feed-main{
        margin-top: 5px;
        margin-bottom: 5px;
        display: flex;
        align-items: center;
        padding: 10px;
        box-shadow: 2px 2px 4px 2px var(--color-shadow);
        border-radius: 5px;
    }
    div#feed-main:hover{
        transform: scale(1.005, 1.005);
        transition: all 0.1s ease;
        box-shadow: 2px 2px 4px 3px var(--color-shadow);
    }
    .articleBlock{
        width: 90vw;
        max-width: 1200px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        text-align: justify;
        gap: 0.3em;
    }
    div.titleBlock{
        display: flex;
        flex-direction: row;
        justify-content: flex-start;
        text-align: start;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.25em;
    }
    label.titleId{
        color: rgba(26, 196, 208, 0.789);
    }
    .pubCount{
        color: rgba(26, 196, 208, 0.789);
    }
    span.authorSpan{
        display: inline-block;
        padding-left: 0.25em;
        padding-right: 0.25em;
    }
    div.actions{
        display: flex;
        flex-direction: row;
        justify-content: flex-start;
        gap: 1em;
    }

    #relatedArticles{
        display: flex;
        flex-direction: row;
        justify-content:space-between;
        align-items: center;
        width: 100%;
    }
    label.relatedArticleScore{
        border-radius: 5px;
        padding-left: 5px;
        padding-right: 5px;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: var(--color-background-theme-highlight);
    }
</style>