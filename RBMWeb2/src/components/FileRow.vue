
<script setup lang="ts">

    import { ref, computed } from 'vue';
    import FileRowMore from './FileRowMore.vue';
    import { isChildDOMElement } from '../core/misc';
    import { useDataStore } from './store';

    const NOTE_FULLSHOW_THRESHOLD = 12;
    const NOTE_SHOW_THRESHOLD = 1;

    const props = defineProps<{
        uid: string
    }>()

    const dataStore = useDataStore();
    const datapoint = ref(dataStore.database.get(props.uid));

    // record if show more is toggled
    const showMore = ref(false);
    // record if mouse is hovering on authorYear div
    const isHoveringAuthorYear = ref(false);

    // template refs
    const initDiv = ref<HTMLElement | null>(null);
    const moreDiv = ref<HTMLElement | null>(null);

    function clickOnRow(event: Event){
        // check if event target is authorYear div or not
        if ((event.target as HTMLElement).id == "authorYear"){
            // Maybe open doc
            const url = datapoint.value.getOpenDocURL()
            if (url !== ""){
                window.open(url, '_blank')?.focus();
            }
            event.stopPropagation();    // prevent show more
        }
        if (!isChildDOMElement(event.target as HTMLElement, moreDiv.value!)){
            // toggle show more
            showMore.value = !showMore.value;
        }
        else{
            // showMore.value = !showMore.value;
        }
    }

    // related to authorYear div
    function hoverInAuthorYear(){
        isHoveringAuthorYear.value = true;
    }
    function hoverOutAuthorYear(){
        isHoveringAuthorYear.value = false;
    }
    const authorYearText = computed(() => {
        if (!isHoveringAuthorYear.value){
            return datapoint.value.yearAuthor(" :: ");
        }
        else {
            const dp = datapoint.value;
            const docType = dp.docType();
            if (docType === ""){
                return "_"
            }
            else{
                return docType;
            }
        }
    })

</script>

<template>
    <div id="fileRow" class="hoverMaxout101 gradIn2" @click="clickOnRow">
        <div id="init" class="row" ref="initDiv">
            <div id="authorYear" class="row text" @mouseover="hoverInAuthorYear" @mouseleave="hoverOutAuthorYear">
                {{ authorYearText }}
            </div>
            <div id="titleStatus" class="row">
                <div id="statusDiv">
                    <div class="status">
                        <img v-if="datapoint.info.file_type == '.pdf'" src="../assets/icons/pdf_fill.svg" alt="" class="icon">
                        <img v-else-if="datapoint.info.url" src="../assets/icons/cloud_fill.svg" alt="" class="icon">
                        <img v-else src="../assets/icons/dot_fill.svg" alt="" class="icon placeholder">
                    </div>

                    <div class="status">
                        <img v-if="datapoint.info.note_linecount>NOTE_FULLSHOW_THRESHOLD" src="../assets/icons/note_fill.svg" alt="" class="icon">
                        <img v-else-if="datapoint.info.note_linecount>NOTE_SHOW_THRESHOLD" src="../assets/icons/note.svg" alt="" class="icon">
                        <img v-else src="../assets/icons/dot_fill.svg" alt="" class="icon placeholder">
                    </div>
                </div>
                <div id="title" class="text"><p>{{ datapoint.info.title }}</p></div>
            </div>
        </div>
        <div id="more" v-show="showMore" ref="moreDiv">
            <FileRowMore :uid="datapoint.info.uuid"></FileRowMore>
        </div>
    </div>
</template>

<style scoped>
    div.row{
        display: flex;
        align-items: center;
        justify-content: flex-start;
    }
    div#init{
        flex-wrap: wrap;
        column-gap: 10px;
    }
    div#fileRow {
        flex-wrap: wrap;
        border: 1px solid var(--color-border);
        border-radius: 5px;
        padding: 3px;
        padding-left: 5px;
        margin-top: 3px;
        margin-bottom: 3px;
    }
    div#fileRow:hover{
        background-color: var(--theme-hover-highlight-color);
        transition: background-color 0.2s;
    }
    #authorYear{
        width: 250px;
        white-space: nowrap;
        background-color: var(--color-background-soft);
        border-radius: 10px;
        /* margin-top: 3px;
        margin-bottom: 3px; */
        padding: 10px;
        padding-top: 3px;
        padding-bottom: 3px;
    }
    #authorYear:hover{
        text-align: center;
        justify-content: center;
        transition: all 0.25s;
        box-shadow: 0 1px 3px 3px var(--color-shadow);
    }
    #titleStatus{
        column-gap: 8px;
    }
    div.text{
        padding: 0px;
        margin: 0px;
        text-align: left;
        text-overflow: ellipsis;
        overflow: hidden;
    }
    @media (max-width: 1500px){
        div#fileRow{
            flex-direction: column;
            align-items:flex-start;
        }
    }
    @media (max-width: 750px){
        #authorYear{
            width: 180px;
        }
    }
    div#statusDiv, div#title, div.status{
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: flex-start;
    }
    div.status{
        justify-content: center;
        width: 15px;
    }
    img.icon {
        height: 15px;
        filter: invert(0.5) opacity(0.25) drop-shadow(0 0 0 var(--color-border)) ;
    }
    img.placeholder{
        height: 8px
    }
</style>