
<script setup lang="ts">
    import { computed, ref } from 'vue';
    import { DataPoint } from '../../core/dataClass';
    import Splitter from '../common/Splitter.vue';
    import NoteEditor from '../reader/NoteEditor.vue';
    import { volInfoFromBibtex } from '../../utils/misc';
    import { useWindowState } from '@/state/wstate';
    import { useDataStore } from '@/state/store';
    import { useAuthorPapers } from '@/state/authorState';
    import FloatingWindow from '../common/FloatingWindow.vue';
    import FileRowContainer from './FileRowContainer.vue';

    const props = defineProps<{
        datapoint: DataPoint | null,
    }>()

    // this is a datapoint that is guaranteed to be non-null
    const $datapoint = computed(() => props.datapoint?props.datapoint:useDataStore().database.getDummy());

    const volPageInfo = computed(() => {
        if (!props.datapoint) return '';
        return volInfoFromBibtex(props.datapoint.summary.bibtex);
    })

    const authors = computed(() => props.datapoint?.authors || []);
    const { authorPapers: rawAuthorPapers } = useAuthorPapers(authors);
    const authorPapers = computed(() => {
        // remove datapoint itself
        const ret = {} as Record<string, string[]>;
        for (const [author, uids] of Object.entries(rawAuthorPapers.value)) {
            ret[author] = uids.filter(uid => uid !== props.datapoint?.uid);
        }
        return ret;
    });
    const showupAuthor = ref('' as string);

    const {width: winw} = useWindowState();
    const splitterDirection = computed(() => winw.value > 768 ? 'horizontal' : 'vertical');

    const initSplitRatio = winw.value > 768 ? 0.3 : 0.5;

</script>

<template>
    <FloatingWindow :show="showupAuthor.length > 0" @close="showupAuthor = ''">
        <h2 style="font-weight: bold;">
            All entries by {{showupAuthor}}
        </h2>
        <div style="height: 10px"></div> <!-- spacer -->
        <FileRowContainer :uids="rawAuthorPapers[showupAuthor]" />
    </FloatingWindow>

    <Splitter :direction="splitterDirection" :split-ratio="initSplitRatio">
        <template v-slot:a>
            <div id="summary-panel-main">
                <h2 class="title">{{$datapoint.summary.title}}</h2>
                <div class="authors-div">
                    <template v-for="author in authors">
                        <div class="author-container">
                            <span class="author">{{author}}</span>
                            <span class="author-paper-count" v-if="authorPapers[author]?.length > 0"
                                @click="showupAuthor = author"
                            >
                                ({{authorPapers[author].length}})
                            </span>
                        </div>
                    </template>
                </div>
                <div class="publication" v-if="!$datapoint.isDummy()">{{$datapoint.publication + `. (${$datapoint.year})` + (volPageInfo? ', '+volPageInfo:'')}}</div>
                <div class="docsize" v-if="$datapoint.summary.doc_size">
                    <span> {{$datapoint.summary.doc_size}} MB </span>
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

div.authors-div{
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
}

div.author-container{
    display: flex;
    align-items: center;
}

span.author{
    text-decoration: underline;
    text-underline-offset: 3px;
    white-space: nowrap;
    font-size: small;
}

span.author-paper-count{
    font-size: small;
    color: var(--color-text-soft);
    padding-inline: 3px;
    border-radius: 5px;
}

span.author-paper-count:hover{
    cursor: pointer;
    background-color: var(--color-background-soft);
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