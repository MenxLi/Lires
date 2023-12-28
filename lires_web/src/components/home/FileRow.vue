
<script setup lang="ts">

    import { ref, computed, watch } from 'vue';
    import FileRowMore from './FileRowMore.vue';
    import { isChildDOMElement } from '../../core/misc';
    import { DataPoint } from '../../core/dataClass';
    import { openURLExternal } from '../../libs/misc';
    import { ServerConn } from '../../core/serverConn';
    import { useUIStateStore } from '../store';

    import BookmarkFill0 from '../../assets/icons/bookmark_fill0.svg'
    import BookmarkFill1 from '../../assets/icons/bookmark_fill1.svg'

    const NOTE_FULLSHOW_THRESHOLD = 12;
    const NOTE_SHOW_THRESHOLD = 1;

    const props = withDefaults(defineProps<{
        datapoint: DataPoint
        unfoldedIds: string[]     // global unfoldedIds from DataCardContainer
        hoveredIds: string[]      // global hoveredIds from DataCardContainer
        line_number?: number
        compact?: boolean
    }>(), {
        line_number: 0,
        compact: false,
    })

    const emits = defineEmits<{
        (e: "update:unfoldedIds", v: string[]) : void
        (e: "update:hoveredIds", v: string[]) : void
    }>()

    // mutable unfoldedIds
    const g_unfoldedIds = computed({
        get: ()=>props.unfoldedIds,
        set: (v)=>emits("update:unfoldedIds", v)}
    );

    // mutable hoveredIds
    const g_hoveredIds = computed({
        get: ()=>props.hoveredIds,
        set: (v)=>emits("update:hoveredIds", v)}
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
    const leadingStatus = ref<HTMLElement | null>(null);

    // A flag to prevent unfold datacard when click on some elements, set this to true when click on those elements
    // so that clickOnRow can check this flag and prevent show more, while also alow the event to propagate to parent
    let __preventNextUnfold = false;      
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
            // event.stopPropagation();    // prevent show more
            __preventNextUnfold = true;
        }
        if (!isChildDOMElement(event.target as HTMLElement, moreDiv.value!)){
            if (__preventNextUnfold){
                __preventNextUnfold = false;
                return;
            }
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
    watch(isDataCardHover, (newVal) => {
        if (newVal){
            g_hoveredIds.value.push(props.datapoint.summary.uuid);
        }
        else{
            g_hoveredIds.value = g_hoveredIds.value.filter(uid => uid !== props.datapoint.summary.uuid);
        }
        // console.log("hoveredIds: ", g_hoveredIds.value);
    })
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

    function setBookmark(status: boolean){
        const newTags = props.datapoint.summary.tags.slice();
        if (status){
            newTags.push("* Bookmark");
        }
        else{
            newTags.splice(newTags.indexOf("* Bookmark"), 1);
        }

        const uuid = props.datapoint.summary.uuid;
        new ServerConn().editData(uuid, null, newTags).then(
            (summary) => {
                props.datapoint.update(summary);
                useUIStateStore().updateShownData();
            },
            () => useUIStateStore().showPopup("Failed to save", "error")
        )

        __preventNextUnfold = true;
    }

    // shortcut to edit datapoint information
    function shortcutEdit(event: KeyboardEvent){
        if (event.code === "Space" 
            && g_unfoldedIds.value.includes(props.datapoint.summary.uuid)
            && isDataCardHover.value
            && document.activeElement === document.body
            ){
            if (moreComponent.value?.shouldEnableEditDatapoint){
                moreComponent.value?.editThisDatapoint();
                event.preventDefault();
            }
        }
    }
    watch(
        () => g_unfoldedIds.value,
        (newVal) => {
            if (newVal.includes(props.datapoint.summary.uuid)){
                window.addEventListener("keydown", shortcutEdit);
            }
            else{
                window.removeEventListener("keydown", shortcutEdit);
            }
        }
    )
</script>

<template>
    <!-- <div id="fileRow" :class="`gradInFast${(props.compact && !showMore)?' compact':''}`" @click="clickOnRow" @mouseover="isDataCardHover=true" @mouseleave="isDataCardHover=false"  -->
    <div id="fileRow" 
        :class="`${(props.compact && !showMore)?' compact':''}` + `${(showMore)?' unfolded':''}`" 
        @click="clickOnRow" @mouseover="isDataCardHover=true" @mouseleave="isDataCardHover=false" 
        ref="dataCard" :style="{backgroundColor: datacardBackgroundColor}">

        <div id="init" class="row" ref="initDiv">
            
            <div class="left row">
                <div id="leadingStatus" class="row" ref="leadingStatus">
                    <div id="authorYear" class="row text" @mouseover="hoverInAuthorYear" @mouseleave="hoverOutAuthorYear">
                        {{ authorYearText }}
                    </div>
                    <div id="marks">
                        <img v-if="datapoint.summary.tags.includes('* Bookmark')" :src="BookmarkFill1" alt="" class="icon redIcon" @click="()=>setBookmark(false)">
                        <img v-else :src="BookmarkFill0" alt="" class="icon" @click="() => setBookmark(true)">
                    </div>
                </div>
                <div id="title" class="text">{{ datapoint.summary.title }}</div>
                <slot></slot>
            </div>

            <div class="right row">
                <div id="statusDiv">
                    <div class="status">
                        <img v-if="datapoint.summary.has_abstract" src="../../assets/icons/contract.svg" alt="" class="icon">
                        <img v-else src="../../assets/icons/dot_fill.svg" alt="" class="icon placeholder">
                    </div>

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
            </div>
        </div>
        <div id="more" ref="moreDiv">
            <FileRowMore :datapoint="datapoint" :show="showMore" ref="moreComponent"></FileRowMore>
        </div>
    </div>
</template>

<style scoped>
    div.row{
        display: flex;
        align-items: center;
        justify-content: flex-start;
        cursor: default;
    }
    div#init{
        display: flex;
        flex-wrap: nowrap;
        flex-direction: row;
        justify-content: space-between;
    }
    div#init>div.left{
        flex-wrap: nowrap;
        column-gap: 5px;
        overflow: hidden;
    }
    div#marks:hover{
        justify-self: flex-end;
        align-items: flex-end;
        cursor: pointer;
    }
    div#fileRow {
        flex-wrap: wrap;
        border-radius: 0px;
        padding: 3px;
        padding-left: 10px;
        padding-right: 5px;
        width: 100%;
        /* border: 1px solid var(--color-border); */
        /* background-color: var(--color-background-ssoft); */
        /* box-shadow: 0px 1px 2px 0px var(--color-shadow); */
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
        /* margin-left: 5px; */
    }
    #authorYear:hover{
        text-align: center;
        justify-content: center;
        transition: all 0.25s;
        box-shadow: 0 1px 3px 3px var(--color-shadow);
    }
    #leadingStatus{
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
        div#fileRow > div.left{
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
    img.redIcon {
        filter: invert(33%) sepia(92%) saturate(3443%) hue-rotate(0deg) brightness(97%) contrast(101%);
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
    #fileRow.compact #leadingStatus{
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
        div#fileRow.compact #title{
            width: 100%;
        }
        div#init>div.left{
            width: 100%;
            flex-wrap: wrap;
        }
    }
</style>