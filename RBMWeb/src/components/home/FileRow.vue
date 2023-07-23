
<script setup lang="ts">

    import { ref, computed, onActivated, onDeactivated } from 'vue';
    import FileRowMore from './FileRowMore.vue';
    import { isChildDOMElement } from '../../core/misc';
    import { DataPoint } from '../../core/dataClass';
    import { openURLExternal } from '../../libs/misc';

    const NOTE_FULLSHOW_THRESHOLD = 12;
    const NOTE_SHOW_THRESHOLD = 1;

    const props = withDefaults(defineProps<{
        datapoint: DataPoint
        unfoldedIds: string[]     // global unfoldedIds from DataCardContainer
        line_number?: number
        compact?: boolean
    }>(), {
        line_number: 0,
        compact: false,
    })

    const emits = defineEmits<
        (e: "update:unfoldedIds", v: string[]) => void
    >()

    // mutable unfoldedIds
    const g_unfoldedIds = computed({
        get: ()=>props.unfoldedIds,
        set: (v)=>emits("update:unfoldedIds", v)}
    );

    // record if show more is toggled
    // const showMore = ref(false);
    const showMore = computed(() => {
        return g_unfoldedIds.value.includes(props.datapoint.summary.uuid);
    })
    // record if mouse is hovering on authorYear div
    const isHoveringAuthorYear = ref(false);

    // template refs
    const dataCard = ref<HTMLElement | null>(null);
    const initDiv = ref<HTMLElement | null>(null);
    const moreDiv = ref<HTMLElement | null>(null);
    const moreComponent = ref<typeof FileRowMore | null>(null);
    const titleStatus = ref<HTMLElement | null>(null);

    function clickOnRow(event: Event){
        // check if event target is fileRow div or not
        if (!isChildDOMElement(event.target as HTMLElement, dataCard.value!)){
            return;
        }
        // check if event target is authorYear div or not
        if ((event.target as HTMLElement).id == "authorYear"){
            // Maybe open doc
            const url = props.datapoint.getOpenDocURL()
            if (url !== ""){
                openURLExternal(url);
            }
            event.stopPropagation();    // prevent show more
        }
        if (!isChildDOMElement(event.target as HTMLElement, moreDiv.value!)){
            // toggle show more
            if (showMore.value){
                g_unfoldedIds.value = g_unfoldedIds.value.filter(uid => uid !== props.datapoint.summary.uuid);
            }
            else{
                g_unfoldedIds.value = [props.datapoint.summary.uuid];
            }
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
            return props.datapoint.yearAuthor(" :: ");
        }
        else {
            const dp = props.datapoint;
            const docType = dp.docType();
            if (docType === ""){
                return "_"
            }
            else{
                return docType;
            }
        }
    })

    // fileRow Style
    const isDataCardHover = ref(false);
    const datacardBackgroundColor = computed(() => {
        // if is hover
        if (isDataCardHover.value){
            return "var(--color-background-theme-highlight)";
        }
        //if is unfolded
        if (g_unfoldedIds.value.includes(props.datapoint.summary.uuid)){
            return "var(--color-background-theme)";
        }
        // only apply alternate color when compact
        if (!props.compact){
            return "var(--color-background-ssoft)";
        }

        if (props.line_number % 2 == 0){
            return "var(--color-background-ssoft)";
        }
        else{
            return "var(--color-background)";
        }
    })
    // const titleMaxWidth = computed(() => {
    //     if (!titleStatus.value){
    //         return 1000;
    //     }
    //     return titleStatus.value.offsetWidth - 500;
    // })

    // shortcut to edit datapoint information
    function shortcutEdit(event: KeyboardEvent){
        if (event.code === "Space" && g_unfoldedIds.value.includes(props.datapoint.summary.uuid) && moreComponent.value?.shouldEnableEditDatapoint){
            // not working sometimes ... ?
            moreComponent.value?.editThisDatapoint();
            event.preventDefault();
        }
    }
    onActivated(()=>{
        window.addEventListener("keydown", shortcutEdit);
    })
    onDeactivated(()=>{
        window.removeEventListener("keydown", shortcutEdit);
    })
</script>

<template>
    <div id="fileRow" :class="`gradInFast${(props.compact && !showMore)?' compact':''}`" @click="clickOnRow" @mouseover="isDataCardHover=true" @mouseleave="isDataCardHover=false" 
        ref="dataCard" :style="{backgroundColor: datacardBackgroundColor}">
        <div id="init" class="row" ref="initDiv">
            <div id="authorYear" class="row text" @mouseover="hoverInAuthorYear" @mouseleave="hoverOutAuthorYear">
                {{ authorYearText }}
            </div>
            <div id="titleStatus" class="row" ref="titleStatus">
                <div id="statusDiv">
                    <div class="status">
                        <img v-if="datapoint.summary.file_type == '.pdf'" src="../../assets/icons/pdf_fill.svg" alt="" class="icon">
                        <img v-else-if="datapoint.summary.url" src="../../assets/icons/cloud_fill.svg" alt="" class="icon">
                        <img v-else src="../../assets/icons/dot_fill.svg" alt="" class="icon placeholder">
                    </div>

                    <div class="status">
                        <img v-if="datapoint.summary.note_linecount>NOTE_FULLSHOW_THRESHOLD" src="../../assets/icons/note_fill.svg" alt="" class="icon">
                        <img v-else-if="datapoint.summary.note_linecount>NOTE_SHOW_THRESHOLD" src="../../assets/icons/note.svg" alt="" class="icon">
                        <img v-else src="../../assets/icons/dot_fill.svg" alt="" class="icon placeholder">
                    </div>
                </div>
                <div id="title" class="text">{{ datapoint.summary.title }}</div>
                <slot></slot>
            </div>
        </div>
        <Transition name="more">
            <div id="more" ref="moreDiv">
                <FileRowMore :datapoint="datapoint" :show="showMore" ref="moreComponent"></FileRowMore>
            </div>
        </Transition>
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
        /* border: 1px solid var(--color-border); */
        border-radius: 5px;
        padding: 3px;
        padding-left: 5px;
        /* background-color: var(--color-background-ssoft); */
        box-shadow: 0px 1px 2px 0px var(--color-shadow);
    }
    div#fileRow:hover{
        /* background-color: var(--color-background-theme-highlight); */
        box-shadow: 1px 2px 5px 1px var(--color-shadow);
        transition: all 0.2s;
    }
    #authorYear{
        width: 250px;
        min-width: 250px;
        white-space: nowrap;
        background-color: var(--color-background-theme-thin);
        border-radius: 10px;
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
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center;
    }
    div.text{
        padding: 0px;
        margin: 0px;
        text-align: left;
        text-overflow: ellipsis;
        overflow: hidden;
    }
    @media (max-width: 750px){
        div#authorYear{
            width:auto;
            min-width: 10px;
        }
        div#fileRow{
            flex-direction: column;
            align-items:flex-start;
        }
    }
    /* @media (max-width: 750px){
        #authorYear{
            width: 180px;
            min-width: 180px;
        }
    } */
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

    .more-enter-active, .more-leave-active {
        transition: all 0.15s;
    }
    .more-enter-from, .more-leave-to {
        opacity: 0;
    }

    /* Compact layout */
    #fileRow.compact #init{
        flex-wrap: nowrap;
    }
    #fileRow.compact #titleStatus{
        max-width: 100%;
    }
    #fileRow.compact #title{
        display: inline-block;
        white-space: nowrap;
        overflow: hidden;
        /* text-overflow: ellipsis; */
        /* width: v-bind("`$(titleMaxWidth)px`"); */
        /* https://stackoverflow.com/a/69078238/6775765 */
    }
    @media (max-width: 750px){
        #fileRow.compact #init{
            flex-wrap: wrap;
        }
    }
</style>