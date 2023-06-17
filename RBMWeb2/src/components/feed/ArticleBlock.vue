
<script setup lang="ts">
    import type { ArxivArticleWithFeatures } from '../Feed.vue';
    import { ServerConn } from '../../core/serverConn';
    import { useDataStore, formatAuthorName } from '../store';
    import { DataPoint } from '../../core/dataClass';
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
                }
                window.alert(`success: ${arxivId}`)
            },
            ()=>{window.alert(`failed: ${arxivId}, check log for details`)},
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
        </div>
    </div>

    <!-- <div class="sep"></div> -->
</template>

<style scoped>
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

    /* div.sep{
        margin-top: 5px;
        margin-bottom: 5px;
        width: 100%;
        justify-self: center;
        height: 0.1em;
        background-color: var(--color-border);
    } */
</style>
    
