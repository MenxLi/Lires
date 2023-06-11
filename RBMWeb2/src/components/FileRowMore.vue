<script setup lang="ts">
import { ref } from 'vue';
import { useDataStore } from './store';

const props = defineProps<{
    uid: string
}>()

const dataStore = useDataStore();
const datapoint = ref(dataStore.database.get(props.uid))

const abstractParagraph = ref<HTMLParagraphElement|null>(null);

// a function to get the abstract of the datapoint
let abstract: string|null = null;
const setAbstract = async () => {
    const failedPrompt = "<label class='hint'>Not avaliable</label>";
    if (abstract === null || abstract === failedPrompt) {
        abstractParagraph.value!.innerHTML = "Loading...";
        abstract = await datapoint.value.requestAbstract();
    }
    if (abstract.trim() === ""){
        abstract = failedPrompt;
    }
    abstractParagraph.value!.innerHTML = abstract;
}
</script>

<template>
    <div id="moreMain">
        <hr>
        <div class="row" id="buttons">
            <a :href="datapoint.getOpenDocURL()" target="_blank" rel="noopener noreferrer">Open</a>
            <a :href="datapoint.getOpenNoteURL()" target="_blank" rel="noopener noreferrer">Note</a>
            <a :href="datapoint.getOpenSummaryURL()" target="_blank" rel="noopener noreferrer">Summary</a>
        </div>
        <div id="abstract">
            <details>
                <summary @click="setAbstract">Abstract</summary>
                <p ref="abstractParagraph" id="abstractParagraph"></p>
            </details>
        </div>
    </div>
</template>

<style scoped>
    hr{
        margin: 10px;
        border: 1px solid var(--color-border);
    }
    div.row{
        display: flex;
        align-items: center;
        justify-content: center;
    }
    div#moreMain{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-bottom: 10px;
    }
    div#buttons{
        gap: 15px
    }
    label.hint {
        font-size: xx-small;
        color: var(--color-border);
    }
    #abstract{
        max-width: 1200px;
        text-align: justify;
        padding-left: 10px;
        padding-right: 10px;
    }
    #abstract summary{
        font-weight: bold;
        cursor: pointer;
        text-align: center;
    }
</style>