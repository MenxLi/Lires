
<script setup lang="ts">
    import type { FeedDataInfoT } from '../../api/protocol';
    import { utcStamp2LocaleStr } from '../../utils/timeUtils';
    import {useConnectionStore, useDataStore } from '../store';
    import { DataPoint } from '../../core/dataClass';
    import FileRowContainer from '../home/FileRowContainer.vue';
    import FloatingWindow from '../common/FloatingWindow.vue';
    import DataEditor from '../home/DataEditor.vue';
    import { computed, ref } from 'vue';
    import { sortByScore } from '../../core/misc';
    import TagBubbleContainer from '../tags/TagBubbleContainer.vue';

    const props = defineProps<{
        article: FeedDataInfoT,
    }>()
    const dataStore = useDataStore();
    const conn = useConnectionStore().conn;

    const dataEditor = ref(null as null | typeof DataEditor);
    async function showDataEditor(){
        dataEditor.value?.show({
            datapoint: null,
            bibtex: props.article.bibtex,
            tags: [],
            url: props.article.url,
        });
    }

    const allAuthorPapers = ref<Record<string, DataPoint[]>>({});
    async function gatherAuthorPapers(){
        for (let i=0; i<props.article.authors.length; i++){
            const author = props.article.authors[i];
            const authorOtherPubIds = props.article.authors_other_publications[i];
            const dps = await dataStore.database.agetMany(authorOtherPubIds);
            allAuthorPapers.value[author] = dps;
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
        authorPapers.value = allAuthorPapers.value[author];
        if (!authorPapers.value){
            authorPapers.value = [];
        }
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
        conn.filter(
            {
                searchBy: "feature",
                searchContent: props.article.abstract,
                maxResults: 10,
            }
            ).then(
                (res) => {
                    const scores = res.scores;
                    const uuids = res.uids;
                    const sortedDpSc = sortByScore(uuids, scores!);
                    dataStore.database.agetMany(sortedDpSc[0], false).then((dps)=>{
                        relatedArticles.value = dps;
                        // filter out scores of non-exist dps
                        const realExistScores = [];
                        for (const dp of dps){
                            const idx = uuids.indexOf(dp.summary.uuid);
                            if (idx >= 0){ realExistScores.push(scores![idx]); }
                        }
                        relatedArticlesScores.value = realExistScores;
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
                <h2 style="font-weight: bold;">{{ props.article.title }}</h2>
                <div style="display: flex; flex-direction: row; justify-content: center; align-items: center;">
                    <TagBubbleContainer :tags="props.article.tags"></TagBubbleContainer>
                    <label class="titleId">{{ props.article.uuid }}</label>
                </div>
            </div>
            <div class="authors">
                <span v-for="(author, index) in props.article.authors" class="authorSpan">
                    <a class="link" v-if="()=>{article.tags.some((tag)=>tag.startsWith('arxiv'))}"
                        :href="`https://arxiv.org/search/?query=${author}&searchtype=author`" 
                        target="_blank">{{ author }}</a>
                    <label v-else>{{ author }}</label>
                    <a class="pubCount" v-if="authorDatabasePublicationCount[author]" @click="()=>onClickAuthorPubCount(author)">
                        {{ `(${authorDatabasePublicationCount[author]})` }}
                    </a>
                    <span v-if="index < props.article.authors.length - 1">, </span>
                </span>
            </div>
            <div class="actions">
                <a :href="article.url" target="_blank">Link</a> |
                <a :href="`https://arxiv.org/pdf/${article.uuid}.pdf`" target="_blank">PDF</a> |
                <a @click="showDataEditor">Collect</a>
            </div>
            <p>Added: {{ utcStamp2LocaleStr(props.article.time_added, true) }}</p>
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
    a{
        border-radius: 1rem;
        padding-inline: 0.5rem;
        padding-block: 0.2rem;
    }
    a:hover{
        cursor: pointer;
    }
    a.link{
        padding: 0px;
    }
    a.link:hover{
        text-decoration: underline;
        text-underline-offset: 0.1em;
        background-color: rgba(0, 0, 0, 0);
    }
    div#tag-selector{
        padding: 5px;
        padding-left: 10px;
        padding-right: 10px;
    }
    div#feed-main{
        display: flex;
        align-items: center;
        padding: 1rem;
        /* box-shadow: 2px 2px 4px 2px var(--color-shadow); */
        background-color: var(--color-background);
        /* border: 1px solid var(--color-border);
        border-top: 0px; */
        /* border-left: 4px solid var(--color-border); */
        border-left: 5px solid var(--color-background);
        border-bottom: 1px solid var(--color-border);
        border-radius: 5px;
    }
    div#feed-main:hover{
        /* transform: scale(1.005, 1.005); */
        transition: all 0.3s ease;
        /* box-shadow: 2px 2px 4px 3px var(--color-shadow); */
        border-left: 5px solid var(--color-theme);
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
        flex-direction: column;
        /* justify-content: flex-start; */
        align-items: flex-start;
        text-align: start;
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