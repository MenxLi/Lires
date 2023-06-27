
<script setup lang="ts">
    import { ref, onMounted, computed } from 'vue';
    import { DataPoint } from '../../core/dataClass';
    import { DataSearcher } from '../../core/dataClass';
    import type { SearchResultant } from '../../core/protocalT';
    import { ServerConn } from '../../core/serverConn';
    import FileRowContainer from './FileRowContainer.vue';
    import { useDataStore } from '../store';

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

    const serverConn = new ServerConn();
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

        let fromContent = null;
        props.datapoint.fetchAbstract().then((abstract)=>{
            if (abstract){
                fromContent = abstract;
            }
        })
        if (fromContent == null){
            if (aiSummary.value && !aiSummary.value.startsWith("Error") && !aiSummary.value.startsWith("Loading")){
                fromContent = aiSummary.value;
            }
            else{
                throw new Error("No content to search for related articles");
            }
        }

        if (fromContent == '') return;
        const conn = new ServerConn();
        const res = await conn.search("searchFeature", {"pattern": fromContent , "n_return": 6});
        const dps: DataPoint[] = new Array();
        const scores: number[] = new Array();
        for (const dp of dataStore.database.getDataByTags([])){
            if (res[dp.summary.uuid]){
                dps.push(dp);
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

    onMounted(() => {
        requestAISummary(false)
    });

    const _unfoldedIds = ref<string[]>([]);

</script>

<template>
    <div id="main">
        <h2>{{ datapoint.summary.title }}</h2>
        <div class="layout">
            <div id="info">
                <table>
                    <tr>
                        <td><b>Authors</b></td>
                        <td>{{ datapoint.summary.authors.toString() }}</td>
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
                    <b>Summary</b>
                    <div class="button" @click="requestAISummary(true)">&#8635;</div>
                </div>
                <p id="aiSummary" ref="aiSummaryParagraph">{{ aiSummary }}</p>
            </div>
            <FileRowContainer :datapoints="relatedDatapoints" :scores="relatedDatapointsScoresDict" v-model:unfolded-ids="_unfoldedIds"></FileRowContainer>
        </div>
    </div>
</template>

<style scoped>
    #main{
        min-width: 800px;
    }
    .layout{
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        gap: 20px;
    }
    #info{
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
</style>