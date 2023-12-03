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
    import Banner from './common/Banner.vue';
    import BannerIcon from './common/BannerIcon.vue';
    import { ref, onMounted, computed, watch } from 'vue';
    import { useDataStore, useUIStateStore } from './store';
    import { useRoute, useRouter } from 'vue-router';
    import {FileSelectButton} from './common/fragments.tsx'
    import { MenuAttached } from './common/fragments.tsx';

    import splitscreenIcon from '../assets/icons/splitscreen.svg';
    import uploadIcon from '../assets/icons/upload.svg';
    import eyeIcon from '../assets/icons/eye.svg';

    const dataStore = useDataStore();
    const uiStateStore = useUIStateStore();
    const route = useRoute();
    const router = useRouter();
    const uid = computed(() => route.params.id as string)
    const datapoint = ref(dataStore.database.get(uid.value));

    watch(()=>route.params.id, ()=>{
        datapoint.value = dataStore.database.get(route.params.id as string);
        initPage();
    })

    function initPage(){
        // some actions that should be reload when datapoint changes
        uiStateStore.addRecentlyReadDataUID(uid.value);
    }
    initPage();

    const recentReadMenuItems = computed(()=>{
        const ret = [];
        for (const uid of uiStateStore.recentlyReadDataUIDs){
            const datapoint = dataStore.database.get(uid);
            ret.push({
                name: datapoint.authorYear(),
                action: ()=>{
                    router.push('/reader/' + uid)
                }
            })
        }
        return ret;
    })


    // 0: doc only
    // 1: note only
    // 2: doc and note
    const layoutType = ref<number>(2);

    // initialize layoutType according to screen size
    if (window.innerWidth < 800){
        layoutType.value = 0;
    }
    function changeLayout(){
        if (window.innerWidth < 800){
            // only two layouts for small screen
            layoutType.value = (layoutType.value + 1)%2
        } else {
            layoutType.value = (layoutType.value + 1)%3
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
    const previewState = computed(()=>{
        try{ return readerBody.value!.noteEditor.preview} 
        catch(e){ return false; }} // not mounted
    );
    const previewBtnText = computed(()=>previewState.value?"edit":"preview");
    function toggleMarkdownPreview(){
        readerBody.value!.noteEditor.preview = !readerBody.value!.noteEditor.preview;
    }

    onMounted(() => {
        // empty database check 
        if (Object.keys(dataStore.database.data).length === 0){
            useUIStateStore().showPopup("Database not loaded or empty database.", "alert");
            // periodically tries to update datapoint...
            const interval = setInterval(() => {
                useUIStateStore().showPopup("Trying to update datapoint...", "warning", 2000);
                if (Object.keys(dataStore.database.data).length !== 0){
                    clearInterval(interval);
                    datapoint.value = dataStore.database.get(uid.value);
                    useUIStateStore().showPopup("Datapoint updated.", "success", 3000);
                }
            }, 750);
        }
    })

</script>

<template>
    <!-- a tricky way to use FileSelectButton as select-upload agent -->
    <FileSelectButton :action="onUploadNewDocument" ref="fileSelectionBtn" :style="{display: 'none'}"> </FileSelectButton>
    <Banner>
        <div id="bannerOps">
            <BannerIcon :iconSrc="splitscreenIcon" labelText="layout" shortcut="ctrl+r"
                @onClick="changeLayout" title="change layout"></BannerIcon>
            <BannerIcon :iconSrc="uploadIcon" labelText="upload" shortcut="ctrl+u"
                @onClick="()=>fileSelectionBtn!.click()" title="upload a new document"></BannerIcon>
            <BannerIcon :iconSrc="eyeIcon" :labelText="previewBtnText" shortcut="ctrl+p"
                @onClick="toggleMarkdownPreview" title="preview or edit markdown note"></BannerIcon>
            |
            <MenuAttached :menu-items="recentReadMenuItems">
                <p>{{ `${datapoint.authorAbbr()} (${datapoint.summary.year})` }}</p>
            </MenuAttached>
        </div>
    </Banner>
    <div id="main-reader" class="gradIn">
        <ReaderBody :datapoint="datapoint" :layoutType="layoutType" ref="readerBody"></ReaderBody>
    </div>
</template>

<style scoped>
div#main-reader{
    margin-top: 45px;
    height: calc(100vh - 45px);
    padding: 10px;
    padding-top: 5px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: calc(100vw - 10px);
    background-color: var(--color-background);
}
div#bannerOps{
    display: flex;
    align-items: center;
    justify-content: center;
}
</style>