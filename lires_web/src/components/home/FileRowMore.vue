<script setup lang="ts">
import { ref, computed } from 'vue';
import { DataPoint } from '../../core/dataClass';
import DataEditor from './DataEditor.vue';
import { useConnectionStore, useUIStateStore } from '@/state/store';
import FloatingWindow from '../common/FloatingWindow.vue';
import {FileSelectButton} from '../common/fragments.tsx'
import { copyToClipboard } from '../../utils/misc.ts'
import { EditableParagraph } from '../common/fragments.tsx'
import DataSummary from './DataSummary.vue';

const props = defineProps<{
    datapoint: DataPoint
    show: boolean
}>()

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
function wrapCitiation(type: string, text: string){
    return [type, `${text.length>80?text.slice(0, 80)+'...':text}`, text]
}
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
    const uuid = props.datapoint.summary.uuid;
    if (window.confirm(`[IMPORTANT] Delete? \n${props.datapoint.toString()}`)){
        useConnectionStore().conn.deleteDatapoint(uuid).then((_) => {
            uiState.showPopup("Deleted");
        });
    }
}

// editor
const dataEditor = ref<typeof DataEditor | null>(null);
function editThisDatapoint(){
    dataEditor.value!.show({
        datapoint : props.datapoint,
    });
}
// a trigger to enable edit datapoint via shortcut, can be called by parent component
// not enable edit shortcut when editor is shown or abstract paragraph is focused
const shouldEnableEditDatapoint = computed(()=> {
    if (abstractParagraph.value === null){
        return !dataEditor.value!.isShown();
    }
    return (!dataEditor.value!.isShown()) && (!abstractParagraph.value.hasFocus())
});
defineExpose({
    editThisDatapoint,
    deleteThisDatapoint,
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
        }" v-for=" (textwrap, index) in 
        [ 
            wrapCitiation('Title', `${datapoint.summary.title}`),
            wrapCitiation('Author-year', `${datapoint.authorAbbr()} (${datapoint.summary.year})`),
            wrapCitiation('APA', `${datapoint.authorAbbr()} (${datapoint.summary.year}). ${datapoint.summary.title}. ${datapoint.summary.publication}.`),
            wrapCitiation('Bibtex', datapoint.summary.bibtex),
            wrapCitiation('DocURL', datapoint.getRawDocURL()),
            wrapCitiation('Markdown', `[${datapoint.authorAbbr()} (${datapoint.summary.year})](${datapoint.getRawDocURL()})`),
            wrapCitiation('UUID', `${datapoint.summary.uuid}`),
        ] ">
            <div @click="()=>{ copy2clip(textwrap[2]); showCopyCitation=false }" :style="{cursor: 'pointer', display: 'flex', flexDirection: 'row'}">
                <div class="citation-type" :style="{
                    marginLeft: '10px', 
                    marginRight: '10px', 
                    borderRadius: '5px', 
                    backgroundColor: 'var(--color-background-mute)',
                    padding: '3px',
                    fontWeight: 'bold',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    }">
                    {{ textwrap[0] }}
                </div>
                <p class="citation-text" :style="{
                    overflowX: 'hidden',
                    whiteSpace: 'nowrap',
                }">
                    {{ textwrap[1] }}
                </p>
            </div>
            <hr v-if="index !== 6">
        </div>
    </FloatingWindow>
    <DataEditor ref="dataEditor"></DataEditor>
    <Transition name="expand-transition">
    <div id="moreMain" v-if="show">
        <div class="row" id="buttons">
            <router-link :to="`/reader/${props.datapoint.summary.uuid}`">Reader</router-link>
            <a :href="datapoint.url" target="_blank" v-if="datapoint.url">Link</a>
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
            <!-- https://github.com/vuejs/core/issues/10928 -->
            <!-- @vue-ignore -->
            <details @toggle="getAbstract">
                <summary>Abstract</summary>
                <EditableParagraph id="abstractParagraph"  ref="abstractParagraph" :style="{minHeight: '20px', fontFamily: '\'Times New Roman\', Times, serif'}"
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
        gap: 10px
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

    div#actions{
        gap: 10px;
        background-color: var(--color-background-mute);
        margin: 3px;
        padding-block: 5px;
        padding-inline: 50px;
        border-radius: 20px;
        box-shadow: inset 0px 1px 2px 0px var(--color-shadow);
    }

    :deep(a){
        cursor: pointer;
        border-radius: 7px;
        padding-inline: 5px;
        user-select: none;
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
            /* to maximum height */
            max-height: 48px;
            opacity: 0;
        }
        100% {
            max-height: auto;
            opacity: 1;
        }
    }

    @keyframes contract {
        0% {
            max-height: 48px;
            opacity: 1;
        }
        50% {
            max-height: 0px;
            opacity: 0;
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
</style>../../utils/misc.ts../../api/serverConn.ts