<script setup lang="ts">
import { ref } from 'vue';
import { DataPoint } from '../../core/dataClass';
import { useDataStore, useUIStateStore } from '../store';

const props = defineProps<{
    datapoint: DataPoint
}>()

const dataStore = useDataStore();
const uiState = useUIStateStore();

const abstractParagraph = ref<HTMLParagraphElement|null>(null);

// a function to get the abstract of the datapoint
let abstract: string|null = null;
const setAbstract = async () => {
    const failedPrompt = "<label class='hint'>Not avaliable</label>";
    abstractParagraph.value!.innerHTML = "Loading...";
    abstract = await props.datapoint.fetchAbstract();
    if (abstract.trim() === ""){
        abstract = failedPrompt;
    }
    abstractParagraph.value!.innerHTML = abstract;
}

// functions to manage data
function deleteThisDatapoint(){
    if (window.confirm(`Delete? \n${props.datapoint.toString()}`)){
        dataStore.database.delete(props.datapoint.summary.uuid).then(uiState.updateShownData)
    }
}
</script>

<template>
    <div id="moreMain">
        <hr>
        <div class="row" id="buttons">
            <router-link :to="`/reader/${props.datapoint.summary.uuid}`">Reader</router-link>
            <a :href="datapoint.getOpenNoteURL()" target="_blank" rel="noopener noreferrer">Note</a>
            <a :href="datapoint.getOpenSummaryURL()" target="_blank" rel="noopener noreferrer">Summary</a>
            <a href="#" rel="noopener noreferrer" @click="deleteThisDatapoint" class="danger">Delete</a>
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

    a.danger{
        color: var(--color-danger);
    }
    a.danger:hover{
        background-color: var(--color-danger-hover);
    }
</style>