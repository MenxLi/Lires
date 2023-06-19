
<script setup lang="ts">
    import type { ArxivArticleWithFeatures } from '../Feed.vue';
    import { ServerConn } from '../../core/serverConn';
    import { useDataStore, formatAuthorName, useUIStateStore } from '../store';
    import { DataPoint, DataSearcher } from '../../core/dataClass';
    import FileRow from '../home/FileRow.vue';
    import FloatingWindow from '../common/FloatingWindow.vue';
    import { ref } from 'vue';

    const props = defineProps<{
        article: ArxivArticleWithFeatures,
    }>()
    const dataStore = useDataStore();

    function addToRBM(){
        const arxivId = props.article.id;
        new ServerConn().addArxivPaperByID(
                arxivId,
            ).then(
            (dpSummary)=>{
                const db = dataStore.database;
                if (Object.keys(db).length == 0){
                    // db is empty, may happen when database is not loaded
                    // do nothing
                }
                else{
                    // add to database
                    db.add(dpSummary);
                    useUIStateStore().updateShownData();
                }
                useUIStateStore().showPopup(`collected: ${arxivId}`, "success")
            },
            ()=>{
                useUIStateStore().showPopup(`failed to collect: ${arxivId}, check log for details`, "warning")
            },
        )
    }

    function authorDatabasePublicationCount(author: string): null | number{
        const pubMap = dataStore.authorPublicationMap;
        author = formatAuthorName(author);
        if (!(author in pubMap)){
            // the author is not in the database
            return null;
        }
        let count = pubMap[author].length;
        // check if current article is in the database
        // const thisTitle = props.article.title.toLowerCase();
        // if (pubMap[author].some((dp) => dp.summary.title.toLowerCase() === thisTitle)){
        //     count -= 1;
        // }
        // if (count == 0){
        //     return null;
        // }
        return count;
    }

    const showAuthorPapers = ref(false);
    const authorPapers = ref([] as DataPoint[]);
    function onClickAuthorPubCount(author: string){
        author = formatAuthorName(author);
        console.log("check publication of author: ", author);
        authorPapers.value = dataStore.authorPublicationMap[author];
        showAuthorPapers.value = true;
    }

    // related articles
    const relatedArticles = ref([] as DataPoint[]);
    const relatedArticlesScores = ref([] as number[]);
    function queryRelatedArticles(){
        if (relatedArticles.value.length > 0){
            return;
        }
        new ServerConn().search(
            "searchFeature", { pattern: props.article.abstract, n_return: 8 }
            ).then(
                (res) => {
                    const scores = new Array();
                    const uuids = new Array();
                    for (const uid of Object.keys(res)){
                        scores.push(res[uid]?.score);
                        uuids.push(uid);
                    }
                    const sortedDpSc = DataSearcher.sortByScore(uuids, scores);
                    relatedArticles.value = sortedDpSc[0].map((uid) => dataStore.database.get(uid));
                    relatedArticlesScores.value = sortedDpSc[1];
                }
            )
    }

</script>

<template>
    <FloatingWindow v-model:show="showAuthorPapers" title="Publications in the database" @onClose="authorPapers=[]">
        <div id="authorPapers">
            <FileRow v-for="dp in authorPapers" :datapoint="dp"></FileRow>
        </div>
    </FloatingWindow>
    <div id="main" class="gradInFast">
        <div class="articleBlock">
            <div class="titleBlock">
                <h2>{{ props.article.title }}</h2>
                <label class="titleId">{{ props.article.id }}</label>
            </div>
            <div class="authors">
                <label>[Authors] </label>
                <span v-for="(author, index) in props.article.authors" class="authorSpan">
                    <a :href="`https://arxiv.org/search/?query=${author}&searchtype=author`">{{ author }}</a>
                    <a class="pubCount" v-if="authorDatabasePublicationCount(author)" @click="()=>onClickAuthorPubCount(author)">
                        {{ ` (${authorDatabasePublicationCount(author)})` }}
                    </a>
                    <span v-if="index < props.article.authors.length - 1">, </span>
                </span>
            </div>
            <div class="actions">
                <a :href="`https://arxiv.org/abs/${article.id}`">Arxiv</a> |
                <a :href="`https://arxiv.org/pdf/${article.id}.pdf`">PDF</a> |
                <a @click="addToRBM">Collect</a>
            </div>
            <p>Published: {{ props.article.publishedTime }}</p>
            <details>
                <summary>Abstract</summary>
                <p>{{ props.article.abstract }}</p>
            </details>
            <details>
                <summary @click="queryRelatedArticles">Related articles</summary>
                <div id="relatedArticles">
                    <div class="relatedArticle" v-for="(dp, index) in relatedArticles">
                        <FileRow :datapoint="dp">
                            <label class="relatedArticleScore">{{relatedArticlesScores[index].toPrecision(3).slice(0, 4)}}</label>
                        </FileRow>
                    </div>
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
    div#main{
        margin-top: 5px;
        margin-bottom: 5px;
        display: flex;
        align-items: center;
        padding: 10px;
        box-shadow: 2px 2px 4px 2px var(--color-shadow);
        border-radius: 5px;
    }
    div#main:hover{
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

    div.relatedArticle{
        display: flex;
        flex-direction: row;
        justify-content:space-between;
        align-items: center;
        gap: 0.5em;
    }
    div.relatedArticle>*{
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
    
