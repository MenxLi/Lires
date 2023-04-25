
<script setup lang="ts">

    import type { DataPoint } from '@/core/dataClass';

    const NOTE_FULLSHOW_THRESHOLD = 8;
    const NOTE_SHOW_THRESHOLD = 1;

    const props = defineProps<{
        datapoint: DataPoint
    }>()

    function openDataURL(){
        const url = props.datapoint.getOpenDocURL()
        if (url){
            window.open(url);
        }
    }
</script>

<template>
    <div class="row hoverMaxout101" @click="(ev) => openDataURL()">
        <div id="authorYear" class="text">{{ datapoint.yearAuthor(" :: ")}}</div>
        <div id="titleStatus">
            <div id="title" class="text"><p>{{ datapoint.info.title }}</p></div>
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
        </div>
    </div>
</template>

<style scoped>
    div.row {
        display: flex;
        flex-wrap: wrap;
        border: 1px solid var(--color-border);
        border-radius: 5px;
        column-gap: 10px;
        align-items: center;
        justify-content: flex-start;
        padding-left: 3px;
        margin-top: 3px;
        margin-bottom: 3px;
    }
    div.row:hover{
        background-color: var(--theme-hover-hight-color);
    }
    #authorYear{
        width: 250px;
        white-space: nowrap;
        background-color: var(--color-background-soft);
        border-radius: 10px;
        margin: 5px;
        margin-top: 3px;
        margin-bottom: 3px;
        padding: 5px;
        padding-top: 3px;
        padding-bottom: 3px;
    }
    #titleStatus{
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: flex-start;
        gap: 10px;
    }
    div.text{
        padding: 0px;
        margin: 0px;
        text-align: left;
        text-overflow: ellipsis;
        overflow: hidden;
    }
    @media (max-width: 1500px){
        div.row{
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