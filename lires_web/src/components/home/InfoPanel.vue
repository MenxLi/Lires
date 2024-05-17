
<script setup lang="ts">
    import { computed } from 'vue';
    import { DataPoint } from '../../core/dataClass';
    import Splitter from '../common/Splitter.vue';
    import NoteEditor from '../reader/NoteEditor.vue';
    import { volInfoFromBibtex } from '../../utils/misc';
    import { useWindowState } from '@/state/wstate';

    const props = defineProps<{
        datapoint: DataPoint | null,
    }>()
    const volPageInfo = computed(() => {
        if (!props.datapoint) return '';
        return volInfoFromBibtex(props.datapoint.summary.bibtex);
    })

    const {width: winw} = useWindowState();
    const splitterDirection = computed(() => winw.value > 768 ? 'horizontal' : 'vertical');

    const initSplitRatio = winw.value > 768 ? 0.3 : 0.5;


</script>

<template>
    <Splitter :direction="splitterDirection" :split-ratio="initSplitRatio">
        <template v-slot:a>
            <div id="summary-panel-main" v-if="datapoint">
                <h2 class="title">{{datapoint.summary.title}}</h2>
                <div class="author-container">
                    <span class="author" v-for="author in datapoint.authors">{{author}}</span>
                </div>
                <div class="publication">{{datapoint.publication + `. (${datapoint.year})` + (volPageInfo? ', '+volPageInfo:'')}}</div>
                <div class="docsize" v-if="datapoint.summary.doc_size">
                    <span> {{datapoint.summary.doc_size}} MB </span>
                </div>
            </div>
        </template>
        <template v-slot:b>
            <NoteEditor :datapoint="datapoint" />
        </template>
    </Splitter>
</template>

<style scoped>
div#summary-panel-main{
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    text-align: left;
    padding: 10px;
    background-color: var(--color-background);
}

h2.title{
    font-size: 1.2em;
    font-weight: bold;
    margin: 0;
    padding: 0;
}

div.author-container{
    display: flex;
    flex-wrap: wrap;
}

span.author{
    text-decoration: underline;
    text-underline-offset: 3px;
    white-space: nowrap;
    margin-right: 5px;
    font-size: small;
}

div.publication{
    font-style: italic;
    font-size: small;
}

div.docsize span{
    font-size: 0.8em;
    color: var(--color-text-soft);
    padding-inline: 5px;
    padding-block: 2px;
    border-radius: 5px;
    border: 1px solid var(--color-border);
    /* background-color: var(--color-background-soft); */
}
</style>