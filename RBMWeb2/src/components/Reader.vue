<script setup lang="ts">
    import ReaderBody from './reader/ReaderBody.vue';
    import Banner from './common/Banner.vue';
    import BannerIcon from './common/BannerIcon.vue';
    import { ref, onMounted } from 'vue';
    import { useDataStore, useUIStateStore } from './store';
    import { useRoute } from 'vue-router';
    import {FileSelectButton} from './common/fragments.tsx'

    import splitscreenIcon from '../assets/icons/splitscreen.svg';
    import uploadIcon from '../assets/icons/upload.svg';

    const dataStore = useDataStore();
    const route = useRoute();

    const uid = route.params.id as string;
    const datapoint = ref(dataStore.database.get(uid));

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
                    useUIStateStore().showPopup('Document uploaded', 'success');
                },
                ()=>useUIStateStore().showPopup('Failed to upload document', 'error')
            )
        }
        if (datapoint.value!.summary.has_file){
            datapoint.value!.freeDocument().then(
                (summary)=>{datapoint.value!.update(summary); uploadDocument()},
                ()=>useUIStateStore().showPopup('Failed to free document', 'error')
            )
        }
        else{
            uploadDocument();
        }
    }

    // empty database check 
    onMounted(() => {
        if (Object.keys(dataStore.database.data).length === 0){
            useUIStateStore().showPopup("Database not loaded or empty database.", "alert");
            // periodically tries to update datapoint...
            const interval = setInterval(() => {
                useUIStateStore().showPopup("Trying to update datapoint...", "warning", 2000);
                if (Object.keys(dataStore.database.data).length !== 0){
                    clearInterval(interval);
                    datapoint.value = dataStore.database.get(uid);
                    useUIStateStore().showPopup("Datapoint updated.", "success", 3000);
                }
            }, 750);
        }
    })

</script>

<template>
    <!-- a tricky way to use FileSelectButton as select-upload agent -->
    <FileSelectButton :action="onUploadNewDocument" ref="fileSelectionBtn" :style="{display: 'none'}"> </FileSelectButton>
    <div id="main">
        <div id="banner">
            <Banner>
                <div id="bannerOps">
                    <BannerIcon :iconSrc="splitscreenIcon" labelText="change layout" @onClick="changeLayout" title="change layout"></BannerIcon>
                    <BannerIcon :iconSrc="uploadIcon" labelText="upload document" @onClick="()=>fileSelectionBtn!.click()" title="upload a new document"></BannerIcon>
                    |
                    <p>{{ `${datapoint.authorAbbr()} (${datapoint.summary.year})` }}</p>
                </div>
            </Banner>
        </div>
        <ReaderBody :datapoint="datapoint" :layoutType="layoutType"></ReaderBody>
    </div>
</template>

<style scoped>
div#main{
    padding: 10px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 98vw;
    height: 99vh;
    background-color: var(--color-background);
}
div#banner{
    padding-bottom: 10px;
    width: 100%;
}
div#bannerOps{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
}
</style>