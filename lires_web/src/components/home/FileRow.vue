
<script setup lang="ts">

    import { ref, computed, watch } from 'vue';
    import FileRowMore from './FileRowMore.vue';
    import { isChildDOMElement } from '../../core/misc';
    import { DataPoint } from '../../core/dataClass';
    import { openURLExternal, volInfoFromBibtex } from '../../utils/misc';
    import { useConnectionStore, useUIStateStore } from '../store';

    import BookmarkFill0 from '../../assets/icons/bookmark_fill0.svg'
    import BookmarkFill1 from '../../assets/icons/bookmark_fill1.svg'

    const NOTE_FULLSHOW_THRESHOLD = 12;
    const NOTE_SHOW_THRESHOLD = 1;

    const props = withDefaults(defineProps<{
        datapoint: DataPoint
        unfoldedIds: string[]     // global unfoldedIds from DataCardContainer
        hoveredIds: string[]      // global hoveredIds from DataCardContainer
        line_number?: number
        // compact?: boolean
    }>(), {
        line_number: 0,
        // compact: false,
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

    // template refs
    const dataCard = ref<HTMLElement | null>(null);
    const initDiv = ref<HTMLElement | null>(null);
    const moreDiv = ref<HTMLElement | null>(null);
    const moreComponent = ref<typeof FileRowMore | null>(null);

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

    // document type icon
    const docTypeEmoji = computed(() => {
        switch (props.datapoint.dtype){
            case "article": return "📄";
            case "book": return "📚";
            case "incollection": return "📖";
            case "inbook": return "📖";
            case "manual": return "📖";
            case "inproceedings": return "📜";
            case "conference": return "📜";
            case "misc": return "📎";
            case "thesis": return "🎓";
            case "phdthesis": return "🎓";
            case "mastersthesis": return "🎓";
            case "techreport": return "📑";
            case "unpublished": return "📝";

            // below non-standard types
            case "webpage": return "🌐";
            case "online": return "🌐";

            // return question mark for unknown type
            default: return "❔";
        }
    })

    // related to authorYear div
    const authorYearText = computed(() => {
        return props.datapoint.yearAuthor("-");
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
        if (isDataCardHover.value){ return "var(--color-background-theme-highlight)"; }
        //if is unfolded
        if (g_unfoldedIds.value.includes(props.datapoint.summary.uuid)){ return "var(--color-background-theme)"; }
        // else, apply zebra color
        if (props.line_number % 2 == 0){ return "var(--color-background-ssoft)"; }
        else{ return "var(--color-background)"; }
    })

    const volPageInfo = computed(() => {
        return volInfoFromBibtex(props.datapoint.summary.bibtex);
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
        useConnectionStore().conn.updateDatapoint(uuid, {tags: newTags}).then(
            (summary) => {
                props.datapoint.update(summary);
                useUIStateStore().updateShownData();
            },
            () => useUIStateStore().showPopup("Failed to save", "error")
        )

        __preventNextUnfold = true;
    }

    // shortcut to edit datapoint information
    function _shouldEnableShortcut(){
        return g_unfoldedIds.value.includes(props.datapoint.summary.uuid)
            && isDataCardHover.value
            && document.activeElement === document.body
            && moreComponent.value?.shouldEnableEditDatapoint;
    }
    function shortcut(event: KeyboardEvent){
        if (event.code === "Space" && _shouldEnableShortcut()){
            moreComponent.value?.editThisDatapoint();
            event.preventDefault();
        }
        if ((event.code === "Delete" || event.code === "Backspace")&& _shouldEnableShortcut()){
            moreComponent.value?.deleteThisDatapoint();
            event.preventDefault();
        }
    }
    watch(
        () => g_unfoldedIds.value,
        (newVal) => {
            if (newVal.includes(props.datapoint.summary.uuid)){
                window.addEventListener("keydown", shortcut);
            }
            else{
                window.removeEventListener("keydown", shortcut);
            }
        }
    )
</script>

<template>
    <div id="fileRow" 
        :class="`${(showMore)?' unfolded':''}`" 
        @click="clickOnRow" @mouseover="isDataCardHover=true" @mouseleave="isDataCardHover=false" 
        ref="dataCard" :style="{backgroundColor: datacardBackgroundColor}">

        <div id="init" class="row" ref="initDiv">
            <div class="left" :style="{
                display: 'flex',
                flexDirection: 'row',
                alignItems: 'center',
                justifyContent: 'flex-start',
                flexWrap: 'nowrap',
                gap: '0.25rem',
            }">
                <div id="marks">
                    <img v-if="datapoint.summary.tags.includes('* Bookmark')" :src="BookmarkFill1" alt="" class="icon redIcon" @click="()=>setBookmark(false)" style="height: 1rem;">
                    <img v-else :src="BookmarkFill0" alt="" class="icon" @click="() => setBookmark(true)" style="height: 1rem;">
                </div>
                <div class="row text">
                    <div :style="{
                        borderRadius: '10px',
                        marginLeft: '5px',
                        display: 'flex',
                        flexDirection: 'column',
                    }">
                        <div id="title" :style="{
                            display: 'flex',
                            fontSize: '1rem',
                        }">
                            <p>
                                <span style="margin-right: 0.25rem; margin-top: 0.25rem; font-size: 0.75rem; opacity: 0.8; display: inline-block; filter:drop-shadow(1px 1px 0.5px var(--color-border));">
                                    {{ docTypeEmoji }}
                                </span>
                                {{ datapoint.summary.title }}
                            </p>
                        </div>
                        <div :style="{
                            marginTop: '0px',
                            padding: '0px',
                            color: 'var(--color-text-soft)',
                            fontSize: '0.75rem',
                        }"> {{ authorYearText + ', ' + datapoint.publication + (volPageInfo?'. '+volPageInfo:'') }} </div>
                    </div>
                    <slot></slot>
                </div>
            </div>

            <div class="right row">
                <div id="statusDiv" :style="{
                    display: 'flex',
                    flexDirection: 'row',
                    alignItems: 'center',
                    gap: '2px',
                }">
                    <div class="status">
                        <img v-if="datapoint.summary.has_abstract" src="../../assets/icons/contract.svg" alt="" class="icon">
                        <img v-else src="../../assets/icons/dot_fill.svg" alt="" class="icon placeholder">
                    </div>

                    <div class="status">
                        <img v-if="datapoint.fileType() == 'pdf'" src="../../assets/icons/pdf_fill.svg" alt="" class="icon">
                        <img v-else-if="datapoint.fileType() == 'html'" src="../../assets/icons/cloud_fill.svg" alt="" class="icon">
                        <img v-else-if="datapoint.fileType() == 'url'" src="../../assets/icons/cloud.svg" alt="" class="icon">
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
        cursor: pointer;
    }
    div#fileRow {
        border-radius: 0px;
        padding: 3px;
        padding-inline: 10px;
        width: 100%;
    }
    div.text{
        padding: 0px;
        margin: 0px;
        text-align: left;
        text-overflow: ellipsis;
        overflow: hidden;
    }
    div.status{
        display: flex;
        align-items: center;
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
    img.icon.big {
        height: 20px;
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

    #title{
        display: inline-block;
        white-space: wrap;
        word-break: break-word;
        overflow: hidden;
        text-overflow: ellipsis;
        /* width: v-bind("`$(titleMaxWidth)px`"); */
        /* https://stackoverflow.com/a/69078238/6775765 */
    }

    @media (max-width: 750px){
        div#init>div.left{
            width: 100%;
            flex-wrap: wrap;
        }
    }
</style>