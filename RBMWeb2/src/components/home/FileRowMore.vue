<script setup lang="ts">
import { ref } from 'vue';
import { DataPoint } from '../../core/dataClass';
import DataEditor from './DataEditor.vue';
import { useDataStore, useUIStateStore } from '../store';
import FloatingWindow from '../common/FloatingWindow.vue';
import {FileSelectButton} from '../common/fragments.tsx'
import {isVisiable} from '../../libs/misc.ts'

const props = defineProps<{
    datapoint: DataPoint
    show: boolean
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

const showCopyCitation = ref(false);
function copy2clip(text: string){
    navigator.clipboard.writeText(text).then(
        () => uiState.showPopup("Copied to clipboard.", "info"),
        () => uiState.showPopup("Failed to copy", "error")
    )
}

// actions
const showActions = ref(false);
function uploadDocument(f: File){
    uiState.showPopup('uploading...');
    props.datapoint.uploadDocument(f).then(
        (summary)=>{props.datapoint.update(summary); uiState.showPopup('Document uploaded', 'success')},
        ()=>uiState.showPopup('Failed to upload document', 'error')
    )
}

function freeDocument(){
    if (!window.confirm(`Free document? \n${props.datapoint.toString()}`)){
        return;
    }
    props.datapoint.freeDocument().then(
        (summary)=>{props.datapoint.update(summary); uiState.showPopup('Document deleted', 'info')},
        ()=>uiState.showPopup('Failed to free document', 'error')
    )
}

function deleteThisDatapoint(){
    if (window.confirm(`[IMPORTANT] Delete? \n${props.datapoint.toString()}`)){
        dataStore.database.delete(props.datapoint.summary.uuid).then(uiState.updateShownData)
    }
}

// editor
const showEditor = ref(false);
function editThisDatapoint(){
    // uiState.showPopup("Not implemented yet", "warning");
    showEditor.value = true;
}
// show editor by pressing space
const moreDiv = ref(null as HTMLDivElement|null);
window.addEventListener("keydown", (e) => {
    // may prevent input space, may need to be fixed in the future
    if (e.code === "Space" && props.show && isVisiable(moreDiv.value!) && !showEditor.value){
        editThisDatapoint();
        // stop the space from scrolling the page
        e.preventDefault();
    }
})
</script>


<template>
    <FloatingWindow v-model:show="showCopyCitation" title="Citations">
        <div id="citations" :style="{
            textAlign: 'left',
        }" v-for=" (text, index) in 
        [ 
            `${datapoint.authorAbbr()} (${datapoint.summary.year})`,
            `${datapoint.summary.title}`,
            `${datapoint.summary.title}. ${datapoint.authorAbbr()} (${datapoint.summary.year})`,
            `${datapoint.summary.bibtex}`,
        ] ">
            <p @click="copy2clip(text); showCopyCitation=false" :style="{cursor: 'pointer'}">{{ text }}</p>
            <hr v-if="index !== 3">
        </div>
    </FloatingWindow>
    <DataEditor v-model:show="showEditor" :datapoint="datapoint"></DataEditor>
    <div id="moreMain" v-if="show" ref="moreDiv">
        <div class="row" id="buttons">
            <router-link :to="`/reader/${props.datapoint.summary.uuid}`">Reader</router-link>
            <!-- <a :href="datapoint.getOpenNoteURL()" target="_blank" rel="noopener noreferrer">Note</a> -->
            <a :href="datapoint.getOpenSummaryURL()" target="_blank" rel="noopener noreferrer">Summary</a>
            <a rel="noopener noreferrer" @click="()=>showCopyCitation=!showCopyCitation">Cite</a>
            <a rel="noopener noreferrer" @click="()=>showActions=!showActions">Actions</a>
        </div>
        <Transition name="actions">
            <div class="row" id="actions" v-if="showActions">
                <a rel="noopener noreferrer" @click="editThisDatapoint">Edit</a>
                <FileSelectButton v-if="!datapoint.summary.has_file"
                    :action="(f: File) => uploadDocument(f)" 
                    text="Upload document" :as-link="true"></FileSelectButton>
                <a v-else rel="noopener noreferrer" @click="freeDocument" class="danger">Free document</a>
                <a rel="noopener noreferrer" @click="deleteThisDatapoint" class="danger">Delete</a>
            </div>
        </Transition>
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
        margin-top: 8px;
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

    a:hover{
        cursor: pointer;
    }
    #actions{
        gap: 15px;
        background-color: var(--color-background-mute);
        /* background-color: var(--color-background-theme-thin); */
        /* width: 98%; */
        /* min-width: 50%; */
        margin: 3px;
        padding: 5px;
        padding-left: 50px;
        padding-right: 50px;
        border-radius: 20px;
        box-shadow: inset 0px 1px 2px 0px var(--color-shadow);
    }
    #actions a {
        text-decoration: underline;
        text-underline-offset: 2px;
    }
    #actions {
        /deep/ a{
            text-decoration: underline;
            text-underline-offset: 2px;
        }
    }

    a.danger{
        color: var(--color-danger);
    }
    a.danger:hover{
        background-color: var(--color-danger-hover);
    }

    .actions-enter-active, .actions-leave-active {
        transition: all 0.2s;
    }
    .actions-enter-from, .actions-leave-to {
        opacity: 0;
        transform: translateY(-10px);
    }
</style>../common/fragments.tsx