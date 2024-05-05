<script lang="ts">
// https://github.com/vuejs/rfcs/blob/master/active-rfcs/0040-script-setup.md#automatic-name-inference
export default {
    name: 'Reader',
    inheritAttrs: false,
    customOptions: {}
}
</script>
<script setup lang="ts">
    import ReaderBody from './reader/ReaderBody.vue';
    import Toolbar from './header/Toolbar.vue';
    import ToolbarIcon from './header/ToolbarIcon.vue';
    import { ref, onMounted, watch } from 'vue';
    import { useDataStore, useUIStateStore, useSettingsStore } from './store';
    import { useRoute, useRouter } from 'vue-router';
    import {FileSelectButton} from './common/fragments.tsx'
    import { MenuAttached } from './common/fragments.tsx';

    import splitscreenIcon from '../assets/icons/splitscreen.svg';
    import uploadIcon from '../assets/icons/upload.svg';
    import { DataPoint } from '../core/dataClass';

    const dataStore = useDataStore();
    const uiStateStore = useUIStateStore();
    const route = useRoute();
    const router = useRouter();
    const datapoint = ref(dataStore.database.getDummy());

    async function updateDatapoint(): Promise<void>{
        const dp = await dataStore.database.aget(route.params.id as string);
        if (dp){ datapoint.value = dp; }

        uiStateStore.addRecentlyReadDataUID(dp.uid);
        dataStore.database.agetMany(uiStateStore.recentlyReadDataUIDs).then((dps)=>{
            updateRecentReadMenuItems(dps);
        })
        console.log("Reader: updated datapoint", dp.summary.title, "uid", dp.uid);
    }

    watch(()=>route.params.id, ()=>{
        updateDatapoint();
    })

    const recentReadMenuItems = ref([] as {name: string, action: ()=>void}[])
    function updateRecentReadMenuItems(dps: DataPoint[]){
        const ret = [];
        for (const dp of dps){
            if (dp.summary.uuid === route.params.id) continue;
            ret.push({
                name: dp.authorYear(),
                action: ()=>{ router.push('/reader/' + dp.summary.uuid) }
            })
        }
        console.log("Reader: updated recent read menu items", ret);
        recentReadMenuItems.value = ret;
    }

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

    // preview
    const readerBody = ref<typeof ReaderBody | null>(null);

    onMounted(() => {
        // empty database check 
        console.log("Reader mounted");
        updateDatapoint();
    })

</script>

<template>
    <!-- a tricky way to use FileSelectButton as select-upload agent -->
    <FileSelectButton :action="onUploadNewDocument" ref="fileSelectionBtn" :style="{display: 'none'}"> </FileSelectButton>
    <Toolbar :compact="true" :show-navigator="false">
        <div id="toolbarOps">
            <ToolbarIcon :iconSrc="splitscreenIcon" labelText="layout" shortcut="ctrl+r"
                @onClick="changeLayout" title="change layout"></ToolbarIcon>
            <ToolbarIcon :iconSrc="uploadIcon" labelText="replace" shortcut="ctrl+u"
                @onClick="()=>fileSelectionBtn!.click()" title="upload a new document"></ToolbarIcon>
            <MenuAttached :menu-items="recentReadMenuItems">
                <div id="recently-read">
                    {{ `${datapoint.authorAbbr()} (${datapoint.summary.year})` }}
                </div>
            </MenuAttached>
        </div>
    </Toolbar>
    <div id="main-reader" class="gradIn">
        <ReaderBody :datapoint="(datapoint as DataPoint)" :layoutType="layoutType" ref="readerBody"></ReaderBody>
    </div>
</template>

<style scoped>
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
div#toolbarOps{
    display: flex;
    align-items: center;
    justify-content: center;
}
div#recently-read{
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0px 10px;
    border-radius: 5px;
    background-color: var(--color-background);
    color: var(--color-text);
    font-size: 0.8em;
    font-weight: bold;
    cursor: pointer;
    text-wrap: nowrap;
    white-space: nowrap;
    overflow-x: hidden;
}
</style>