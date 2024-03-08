
<script setup lang="ts">
    import { ref, onMounted, computed } from 'vue';
    import { DataPoint } from '../../core/dataClass';
    import { DataSearcher } from '../../core/dataClass';
    import type { SearchResultant } from '../../api/protocalT';
    import FileRowContainer from './FileRowContainer.vue';
    import {useConnectionStore, useDataStore} from '../store';

    const props = defineProps<{
        datapoint: DataPoint
    }>()

    const dataStore = useDataStore();
    const relatedDatapoints = ref<DataPoint[]>([]);
    const relatedDatapointsScores = ref<number[]>([]);
    const relatedDatapointsScoresDict = computed<Record<string, string>>(
        ()=>Object.fromEntries(
            relatedDatapoints.value.map((dp, i)=>[
                dp.summary.uuid, relatedDatapointsScores.value[i].toPrecision(3)
            ])
        )
    );

    const serverConn = useConnectionStore().conn;
    const aiSummaryParagraph = ref<HTMLParagraphElement | null>(null);
    const aiSummary = ref<string>('');

    function requestAISummary(force: boolean = false){
        aiSummary.value = 'Loading...';
        let _summary = "";
        serverConn.reqAISummary(
            props.datapoint.summary.uuid,
            (data: string) => {
                data.replace(/\\n/g, '<br>');
                _summary += data;
                aiSummary.value = _summary;
            },
            () => {
                updateRelatedArticles()
                console.log('finished');
            },
            force
        );
    }

    async function updateRelatedArticles(){

        let fromContent: string | null = null;
        if (props.datapoint.supp.abstract){
            fromContent = props.datapoint.supp.abstract;
        }
        else{
            fromContent = await props.datapoint.fetchAbstract()
        }

        if (!fromContent){
            if (aiSummary.value && !aiSummary.value.startsWith("Error") && !aiSummary.value.startsWith("Loading")){
                fromContent = aiSummary.value;
            }
            else{
                throw new Error("No content to search for related articles");
            }
        }

        if (fromContent == '') return;
        const res = await serverConn.search("searchFeature", {"pattern": fromContent , "n_return": 9});
        const dps: DataPoint[] = await dataStore.database.agetMany(Object.keys(res));
        const scores: number[] = new Array();
        for (const dp of dps){
            if (res[dp.summary.uuid]){
                const score = (res[dp.summary.uuid] as SearchResultant).score as number;   // score exists on feature search
                scores.push(score);
            }
        }
        [relatedDatapoints.value, relatedDatapointsScores.value] = DataSearcher.sortByScore(
            dps, scores, false
        );
        if (relatedDatapoints.value && relatedDatapoints.value[0].summary.uuid == props.datapoint.summary.uuid){
            // remove self
            relatedDatapoints.value.shift();
            relatedDatapointsScores.value.shift();
        }
    }

    const showAuthorPapers = ref("");
    const authorPapers = ref([] as DataPoint[]);

    const allAuthorPapers = ref<Record<string, DataPoint[]>>({});
    async function gatherAuthorPapers(){
        const allAuthors = props.datapoint.authors;
        const allPubs = await Promise.all(allAuthors.map((author) => {
            return dataStore.database.agetByAuthor(author);
        }))
        allAuthorPapers.value = {};
        for (let i = 0; i < allAuthors.length; i++){
            allAuthorPapers.value[allAuthors[i]] = allPubs[i];
        }
    }

    const authorDatabasePublicationCount = computed(()=>{
        // return a map of author to publication count
        const res: Record<string, number | null> = {};
        for (const author in allAuthorPapers.value){
            if (allAuthorPapers.value[author] && allAuthorPapers.value[author].length > 1){
                res[author] = allAuthorPapers.value[author].length - 1;
            }
            else{
                res[author] = null;
            }
        }
        return res;
    })

    function onClickAuthorPubCount(author: string){
        // author = formatAuthorName(author);
        authorPapers.value = allAuthorPapers.value[author];
        if (!authorPapers.value){
            authorPapers.value = [];
        }
        // remove self from authorPapers
        authorPapers.value = authorPapers.value.filter((dp)=>dp.summary.uuid != props.datapoint.summary.uuid);
        if (showAuthorPapers.value === author){
            showAuthorPapers.value = "";
        }
        else{ showAuthorPapers.value = author; }
    }

    onMounted(() => {
        gatherAuthorPapers();
        requestAISummary(false)
    });

    const initWidth = computed(()=>{
        const maxW = 1200;      // max width

        // full screen at fullScreenAt, 
        // max width at maximizeAt,
        const maximizeAt = 2400;
        const fullScreenAt = 600;

        const perc = Math.min(Math.max(window.innerWidth - fullScreenAt, 0) / (maximizeAt - fullScreenAt), 1)
        const x = (perc - 0.5) * Math.PI    // 0.5 -> 0, 1 -> PI/2
        const borderW = (Math.sin(x) + 1)*0.5 * (maximizeAt - maxW)
        const borderW_integer = Math.round(borderW)
        return `${window.innerWidth - borderW_integer}px`
    });

</script>

<template>
    <div id="main" :style="{width: initWidth}">
        <h2>{{ datapoint.summary.title }}</h2>
        <div class="layout">
            <div id="info">
                <table>
                    <tr>
                        <td><b>Authors</b></td>
                        <td id="authorTD">
                            <div v-for="author in datapoint.summary.authors">
                                <span>{{ author }}</span>
                                <a v-if="authorDatabasePublicationCount[author] !== null" @click="()=>onClickAuthorPubCount(author)">
                                    ({{ authorDatabasePublicationCount[author] }})
                                </a>
                            </div>
                        </td>
                    </tr>
                    <Transition name="slideDown">
                    <tr v-if="showAuthorPapers" id="otherPubTR">
                        <td colspan="2">
                            <b>{{ `Other publications from ${showAuthorPapers.toUpperCase()}:` }}</b>
                            <div id="authorPapers">
                                <FileRowContainer :uids=" authorPapers.map((dp)=>dp.summary.uuid) "></FileRowContainer>
                            </div>
                        </td>
                    </tr>
                    </Transition>
                    <tr>
                        <td><b>Publication</b></td>
                        <td>{{ datapoint.summary.publication }}</td>
                    </tr>
                    <tr>
                        <td><b>Year</b></td>
                        <td>{{ datapoint.summary.year }}</td>
                    </tr>
                    <tr>
                        <td><b>Tags</b></td>
                        <td>{{ datapoint.summary.tags.toString() }}</td>
                    </tr>
                    <tr>
                        <td><b>Type</b></td>
                        <td>{{ datapoint.docType() + `${datapoint.summary.has_file?
                            ' (' + datapoint.summary.doc_size.toString() + 'M)':''}` }}</td>
                    </tr>
                    <!-- <tr>
                        <td><b>Modified</b></td>
                        <td>{{ datapoint.summary.time_modified }}</td>
                    </tr> -->
                </table>
            </div>
            <div id="shortSummary">
                <div id="shortSummaryTitle">
                    <b>AI Summary</b>
                    <div class="button" @click="requestAISummary(true)">&#8635;</div>
                </div>
                <p id="aiSummary" ref="aiSummaryParagraph">{{ aiSummary }}</p>
            </div>
            <details>
                <summary><b>Related Articles</b></summary>
                <FileRowContainer :uids="
                    relatedDatapoints.map((dp)=>dp.summary.uuid)
                " :scores="relatedDatapointsScoresDict"></FileRowContainer>
            </details>
        </div>
    </div>
</template>

<style scoped>
    .layout{
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        gap: 20px;
    }
    #info{
        width: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: flex-start;
        text-align: left;
    }
    b{
        font-weight: bold;
    }
    #shortSummary{
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: left;
    }
    #shortSummaryTitle{
        display: flex;
        flex-direction: row;
        justify-content: flex-start;
        align-items: center;
        gap: 10px;
    }
    .button{
        cursor: pointer;
        border-radius: 3px;
    }
    .button:hover{
        background-color: var(--color-background-theme-highlight);
    }
    details{
        width: 100%;
    }

    table{
        width: 100%
    }
    td{
        vertical-align: top;
        padding-left: 5px;
        padding-right: 5px;
    }
    td#authorTD{
        display: flex;
        flex-direction: row;
        justify-content: flex-start;
        align-items: flex-start;
        flex-wrap: wrap;
        gap: 10px;
    }
    td#authorTD div{
        display: block;
    }
    tr#otherPubTR td{
        width: 100%;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid var(--color-border);
        background-color: var(--color-background-mute);
        /* box-shadow: 0px 0px 5px var(--color-shadow); */
    }
    .slideDown-enter-active, .slideDown-leave-active {
        transition: all 0.15s ease;
    }
    .slideDown-enter-from, .slideDown-leave-to {
        transform: translateY(-10%);
        opacity: 0;
    }
</style>../../api/protocalT../../api/serverConn