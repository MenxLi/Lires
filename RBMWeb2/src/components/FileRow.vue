
<script setup lang="ts">

    import { ref, computed } from 'vue';
    import type { DataPoint } from '@/core/dataClass';

    const NOTE_FULLSHOW_THRESHOLD = 12;
    const NOTE_SHOW_THRESHOLD = 1;

    const props = defineProps<{
        datapoint: DataPoint
    }>()

    function openDataURL(event: Event){
        // check if event target is authorYear div or not
        let url = "";
        if ((event.target as HTMLElement).id == "authorYear"){
            if (props.datapoint.info.note_linecount > NOTE_SHOW_THRESHOLD){
                url = props.datapoint.getOpenNoteURL()
            }
            event.stopPropagation();    // prevent open doc
        }
        else{
            url = props.datapoint.getOpenDocURL()
        }
        if (url !== ""){
            window.open(url, '_blank')?.focus();
        }
    }

    // record if mouse is hovering on authorYear div
    const isHoveringAuthorYear = ref(false);
    function hoverInAuthorYear(){
        isHoveringAuthorYear.value = true;
    }
    function hoverOutAuthorYear(){
        isHoveringAuthorYear.value = false;
    }
    const authorYearText = computed(() => {
        if (!isHoveringAuthorYear.value){
            return props.datapoint.yearAuthor(" :: ");
        }
        else if(props.datapoint.info.note_linecount <= NOTE_SHOW_THRESHOLD){
            return "_"
        }
        else{
            return "NOTE";
        }
    })

</script>

<template>
    <div id="fileRow" class="row hoverMaxout101 gradIn2" @click="openDataURL">
        <div id="authorYear" class="row text" @mouseover="hoverInAuthorYear" @mouseleave="hoverOutAuthorYear">
            {{ authorYearText }}
        </div>
        <div id="titleStatus" class="row">
            <div id="statusDiv">
                <div class="status">
                    <img v-if="datapoint.info.file_type == '.pdf'" src="@/assets/icons/pdf_fill.svg" alt="" class="icon">
                    <img v-else-if="datapoint.info.url" src="@/assets/icons/cloud_fill.svg" alt="" class="icon">
                    <img v-else src="@/assets/icons/dot_fill.svg" alt="" class="icon placeholder">
                </div>

                <div class="status">
                    <img v-if="datapoint.info.note_linecount>NOTE_FULLSHOW_THRESHOLD" src="@/assets/icons/note_fill.svg" alt="" class="icon">
                    <img v-else-if="datapoint.info.note_linecount>NOTE_SHOW_THRESHOLD" src="@/assets/icons/note.svg" alt="" class="icon">
                    <img v-else src="@/assets/icons/dot_fill.svg" alt="" class="icon placeholder">
                </div>
            </div>
            <div id="title" class="text"><p>{{ datapoint.info.title }}</p></div>
        </div>
    </div>
</template>

<style scoped>
    div.row{
        display: flex;
        align-items: center;
        justify-content: flex-start;
    }
    div#fileRow {
        flex-wrap: wrap;
        border: 1px solid var(--color-border);
        border-radius: 5px;
        padding: 3px;
        padding-left: 5px;
        margin-top: 3px;
        margin-bottom: 3px;
        column-gap: 10px;
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