<script setup lang="ts">
import { ref, computed } from 'vue';
import { DataPoint } from '../../core/dataClass';
import DataEditor from './DataEditor.vue';
import { useDataStore, useUIStateStore } from '../store';
import FloatingWindow from '../common/FloatingWindow.vue';
import {FileSelectButton} from '../common/fragments.tsx'
import { copyToClipboard } from '../../libs/misc.ts'
import { EditableParagraph } from '../common/fragments.tsx'
import DataSummary from './DataSummary.vue';

const props = defineProps<{
    datapoint: DataPoint
    show: boolean
}>()

const dataStore = useDataStore();
const uiState = useUIStateStore();

const abstractParagraph = ref<typeof EditableParagraph|null>(null);

// a function to get the abstract of the datapoint
const getAbstract = async (ev: Event) => {
    if (ev.target instanceof HTMLDetailsElement){
        if (!ev.target.open){ return; }
    }
    abstractParagraph.value!.setEditable(false);
    abstractParagraph.value!.innerText = "Loading...";
    props.datapoint.fetchAbstract().then(
        (abstract: string) => {
            abstractParagraph.value!.innerText = abstract;
            abstractParagraph.value!.setEditable(true);
        },
        () => {
            abstractParagraph.value!.innerText = "Failed to load abstract.";
        }
    );
}
const onSetAbstract = async (t: string) => {
    if (!t){ return; }
    await props.datapoint.uploadAbstract(t);
    await props.datapoint.update();     // update datapoint summary abstract status
}

const showCopyCitation = ref(false);
function copy2clip(text: string){
    copyToClipboard(text).then(
        (success: boolean) => {
            if (!success){ uiState.showPopup("Failed to copy to clipboard.", "error") }
            else{ uiState.showPopup("Copied to clipboard.", "info") }
        },
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
// a trigger to enable edit datapoint via shortcut, can be called by parent component
// not enable edit shortcut when editor is shown or abstract paragraph is focused
const shouldEnableEditDatapoint = computed(()=> {
    if (abstractParagraph.value === null){
        return !showEditor.value;
    }
    return (!showEditor.value) && (!abstractParagraph.value.hasFocus())
});
defineExpose({
    editThisDatapoint,
    shouldEnableEditDatapoint
})
// summary
const showSummary = ref(false);
</script>


<template>
    <FloatingWindow v-model:show="showSummary" title="Summary">
        <DataSummary :datapoint="datapoint"></DataSummary>
    </FloatingWindow>
    <FloatingWindow v-model:show="showCopyCitation" title="Citations">
        <div id="citations" :style="{
            textAlign: 'left',
        }" v-for=" (text, index) in 
        [ 
            `${datapoint.authorAbbr()} (${datapoint.summary.year})`,
            `${datapoint.summary.title}`,
            `${datapoint.summary.title}. ${datapoint.authorAbbr()} (${datapoint.summary.year})`,
            `${datapoint.summary.bibtex}`,
            `${datapoint.getRawDocURL()}`,
        ] ">
            <p @click="copy2clip(text); showCopyCitation=false" :style="{cursor: 'pointer'}" v-if="index===3">{{
                `[Bibtex] ${text.slice(0, 50)}...`
            }}</p>
            <p @click="copy2clip(text); showCopyCitation=false" :style="{cursor: 'pointer'}" v-else-if="index===4">{{
                `[DocURL] ${text.slice(0, 50)}...`
            }}</p>
            <p @click="copy2clip(text); showCopyCitation=false" :style="{cursor: 'pointer'}" v-else>{{
                text
            }}</p>
            <hr v-if="index !== 4">
        </div>
    </FloatingWindow>
    <DataEditor v-model:show="showEditor" :datapoint="datapoint"></DataEditor>
    <Transition name="expand-transition">
    <div id="moreMain" v-if="show">
        <div class="row" id="buttons">
            <router-link :to="`/reader/${props.datapoint.summary.uuid}`">Reader</router-link>
            <!-- <a :href="datapoint.getOpenNoteURL()" target="_blank" rel="noopener noreferrer">Note</a> -->
            <!-- <a :href="datapoint.getOpenSummaryURL()" target="_blank" rel="noopener noreferrer">Summary</a> -->
            <a rel="noopener noreferrer" @click="()=>showSummary=!showSummary">Summary</a>
            <a rel="noopener noreferrer" @click="()=>showCopyCitation=!showCopyCitation">Cite</a>
            <a rel="noopener noreferrer" @click="()=>showActions=!showActions">Actions</a>
        </div>
        <Transition name="actions">
            <div class="row" id="actions" v-if="showActions">
                <a rel="noopener noreferrer" class="btn" @click="editThisDatapoint">Edit</a>
                <FileSelectButton v-if="!datapoint.summary.has_file"
                    :action="(f: File) => uploadDocument(f)" 
                    text="Upload document" :as-link="true"></FileSelectButton>
                <a v-else rel="noopener noreferrer" @click="freeDocument" class="danger btn">Free document</a>
                <a rel="noopener noreferrer" @click="deleteThisDatapoint" class="danger btn">Delete</a>
            </div>
        </Transition>
        <div id="abstract">
            <details @toggle="getAbstract">
                <summary>Abstract</summary>
                <EditableParagraph id="abstractParagraph"  ref="abstractParagraph" :style="{minHeight: '20px'}"
                    @finish="(t: any)=>onSetAbstract(t)"></EditableParagraph>
            </details>
        </div>
    </div>
    </Transition>
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
        overflow-y: hidden;
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

    :deep(a){
        cursor: pointer;
    }
    :deep(a.btn){
        text-decoration: underline;
        text-underline-offset: 2px;
        cursor: pointer;
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

    /* https://www.cnblogs.com/WindrunnerMax/p/14346468.html */
    @keyframes expand {
        0% {
            max-height: 0px;
            opacity: 0;
            margin: 0px;
        }
        50% {
            /* set a lower max-height, 
            the actuall added height would be around 55-100? */
            /* use 70% of the time to expand to about actual height */
            max-height: 58px;
            opacity: 0;
        }
        75% {
            /* 58 -> 97.x */
            max-height: 100px;
        }
        100% {
            max-height: auto;
            opacity: 1;
        }
    }

    @keyframes contract {
        0% {
            max-height: 58px;
            opacity: 1;
        }
        25% {
            opacity: 0;
        }
        50% {
            max-height: 0px;
        }
        100% {
            margin: 0px;
            max-height: 0px;
            opacity: 0;
        }
    }
    
    .expand-transition-enter-active{
        animation: expand .2s ease-in-out;
    }
    .expand-transition-leave-active {
        /* animation: expand 0.1s reverse; */
        animation: contract .2s ease-in-out;
    }
</style>