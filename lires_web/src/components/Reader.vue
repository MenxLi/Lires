<script lang="ts">
// https://github.com/vuejs/rfcs/blob/master/active-rfcs/0040-script-setup.md#automatic-name-inference
export default {
    name: 'Reader',
    inheritAttrs: false,
    customOptions: {}
}
</script>
<script setup lang="ts">
    import ReaderTab from './reader/ReaderTab.vue';
    import ReaderBody from './reader/ReaderBody.vue';
    import Toolbar from './header/Toolbar.vue';
    import ToolbarIcon from './header/ToolbarIcon.vue';
    import { ref, onMounted, watch, onBeforeUnmount, onUpdated } from 'vue';
    import { useDataStore, useUIStateStore, useSettingsStore } from '../state/store';
    import { useRoute } from 'vue-router';
    import {FileSelectButton} from './common/fragments.tsx'
    import { useWindowState } from '@/state/wstate.ts';

    import splitscreenIcon from '../assets/icons/splitscreen.svg';
    import uploadIcon from '../assets/icons/upload.svg';
    import { DataPoint } from '../core/dataClass';

    const dataStore = useDataStore();
    const uiStateStore = useUIStateStore();
    const route = useRoute();
    const datapoint = ref(dataStore.database.getDummy());
    const recentReadDatapoints = ref([] as DataPoint[]);

    async function updateDatapoint(): Promise<void>{
        const dp = await dataStore.database.aget(route.params.id as string);
        if (dp){ datapoint.value = dp; }

        uiStateStore.addRecentlyReadDataUID(dp.uid);
        dataStore.database.agetMany(uiStateStore.recentlyReadDataUIDs).then((dps)=>{
            dps.reverse();
            recentReadDatapoints.value = dps;
        })
        console.log("Reader: updated datapoint", dp.summary.title, "uid", dp.uid);
    }

    watch(()=>route.params.id, ()=>{
        updateDatapoint();
    })

    // 0: doc only
    // 1: note only
    // 2: doc and note
    const layoutType = ref(useSettingsStore().readerLayoutType);

    // initialize layoutType according to screen size
    if (window.innerWidth < 800){
        layoutType.value = 0;
    }
    function changeLayout(){
        if (window.innerWidth < 800){
            // only full screen layout on small screen
            layoutType.value = (layoutType.value + 1)%2
        } else {
            // since v1.3.1a, remove note-only layout on large screen
            // only document full screen (0) or document side by side with note (2)
            switch (layoutType.value){
                case 0:
                    layoutType.value = 2;
                    break;
                case 1:
                    layoutType.value = 2;
                    break;
                case 2:
                    layoutType.value = 0;
                    break;
            }
        }
    }

    // upload new document
    const fileSelectionBtn = ref<typeof FileSelectButton|null>(null);
    function onUploadNewDocument(f: File){
        function uploadDocument(){
            datapoint.value!.uploadDocument(f).then(
                (summary)=>{
                    datapoint.value!.update(summary); 
                    uiStateStore.showPopup('Document uploaded', 'success');
                },
                ()=>uiStateStore.showPopup('Failed to upload document', 'error')
            )
        }
        if (datapoint.value!.summary.has_file){
            datapoint.value!.freeDocument().then(
                (summary)=>{datapoint.value!.update(summary); uploadDocument()},
                ()=>uiStateStore.showPopup('Failed to free document', 'error')
            )
        }
        else{
            uploadDocument();
        }
    }

    // dynamic tab size
    const wstate = useWindowState();
    const toolbarOpsLeft = ref<HTMLDivElement|null>(null);
    const toolbarOpsRight = ref<HTMLDivElement|null>(null);
    function setToolbarOpsWidth(){
        if (toolbarOpsLeft.value && toolbarOpsRight.value){
            const rightWidth = toolbarOpsRight.value.getBoundingClientRect().width;
            toolbarOpsLeft.value.style.width = `calc(100% - ${rightWidth}px)`;
        }
    }

    // preview
    const readerBody = ref<typeof ReaderBody | null>(null);

    onMounted(() => {
        // empty database check 
        console.log("Reader mounted");
        updateDatapoint();

        // set the width of the left side of the toolbar
        watch([wstate.width, wstate.height], ()=>{
            setToolbarOpsWidth();
        })

        setToolbarOpsWidth();
    })

    onUpdated(() => {
        setToolbarOpsWidth();
    })

    onBeforeUnmount(() => {
        console.log("Reader unmounted");
        wstate.cleanup();
    })

</script>

<template>
    <Toolbar :compact="true" :show-navigator="false">
        <div id="toolbar-ops">
            <div ref="toolbarOpsLeft">
                <ReaderTab 
                :this-datapoint="datapoint as DataPoint" 
                :datapoints="recentReadDatapoints as DataPoint[]"
                ></ReaderTab>
            </div>
            <div class="toolbar-ops-right" ref="toolbarOpsRight">
                <FileSelectButton :action="onUploadNewDocument" ref="fileSelectionBtn" :style="{display: 'none'}"> </FileSelectButton>
                <ToolbarIcon :iconSrc="uploadIcon" labelText="replace" shortcut="ctrl+u"
                    @onClick="()=>fileSelectionBtn!.click()" title="upload a new document"></ToolbarIcon>
                <ToolbarIcon :iconSrc="splitscreenIcon" labelText="layout" shortcut="ctrl+r"
                    @onClick="changeLayout" title="change layout"></ToolbarIcon>
            </div>
        </div>
    </Toolbar>
    <div id="main-reader" class="gradIn">
        <ReaderBody :datapoint="(datapoint as DataPoint)" :layoutType="layoutType" ref="readerBody"></ReaderBody>
    </div>
</template>

<style scoped>
div#toolbar-ops{
    display: flex;
    align-items: center;
    justify-content: flex-end;
    width: 100%;
    height: 100%;
}
div.toolbar-ops-right{
    display: flex;
    align-items: center;
    justify-content: center;
}

div#main-reader{
    bottom: 0px;
    padding-top: 0px;
    position: fixed;
    top: 30px;
    left: 0px;
    right: 0px;
    background-color: var(--color-background);
}
@media only screen and (max-width: 767px) {
    div#main-reader{
        padding: 0px;
    }
}
</style>