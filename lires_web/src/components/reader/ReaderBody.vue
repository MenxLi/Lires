<script setup lang="ts">
    import { onMounted, onUnmounted, ref, watch, computed } from 'vue';
    import { useRouter } from 'vue-router';
    import NoteEditor from './NoteEditor.vue';
    import ReaderChat from './ReaderChat.vue';
    import { useUIStateStore, useSettingsStore } from '@/state/store';
    import { DataPoint } from '../../core/dataClass';
    import { ThemeMode } from '../../core/misc';
    import { FileSelectButton } from '../common/fragments';
    import Splitter from '../common/Splitter.vue';

    const props = defineProps<{
        datapoint: DataPoint,
        layoutType: number,
    }>()

    const router = useRouter();
    const urlHashMarkParam = computed(()=>{
        const query = router.currentRoute.value.query;
        let docHashMark = query['docHashMark'] as string | undefined;
        if (!docHashMark){ docHashMark = '' }
        if (props.datapoint.fileType() == 'pdf' && !docHashMark.includes('pagemode=')){
            // https://github.com/mozilla/pdf.js/wiki/Viewer-options
            docHashMark += '&pagemode=none';
        }
        return docHashMark;
    });

    const iframeKey = ref(0); // to force reload iframe
    const isMovingSplitter = ref<boolean>(false);
    const noteEditor = ref<typeof NoteEditor | null>(null);
    const uiStateStore = useUIStateStore();
    const currentTab = ref<'note' | 'chat'>((uiStateStore.readerActiveTabs[props.datapoint.uid] as 'note' | 'chat') || 'note');
    
    watch(currentTab, (newTab) => {
        uiStateStore.setReaderActiveTab(props.datapoint.uid, newTab);
    });

    watch(() => props.datapoint.uid, (newUid) => {
        const tab = uiStateStore.readerActiveTabs[newUid];
        currentTab.value = tab || 'note';
    });

    // const togglePreview = (state: boolean)=>{ noteEditor.value!.togglePreview(state);}
    
    function refresh(){
        iframeKey.value += 1;
    }
    
    defineExpose({
        noteEditor,
        refresh
    });

    function setLayout(layoutType: number){
        useSettingsStore().setReaderLayoutType(layoutType);
    }
    watch(() => props.layoutType, (newLayoutType, oldLayoutType) => {
        console.log('layoutType changed:', oldLayoutType, "->", newLayoutType);
        setLayout(newLayoutType);
    });

    const theme = ref(ThemeMode.isDarkMode()?'dark':'light' as 'dark'|'light')
    ThemeMode.registerThemeChangeCallback(()=>theme.value = ThemeMode.isDarkMode()?'dark' : 'light')
    const openDocURL = computed(()=>`${props.datapoint.getOpenDocURL({
            extraPDFViewerParams: { "color-mode": theme.value, },
            urlHashMark: urlHashMarkParam.value,
        })}`)
    
    const handleMessage = async (event: MessageEvent) => {
        if (event.data && event.data.type === 'PDF_SAVE') {
            const blob = event.data.blob;
            let filename = event.data.filename || 'annotated.pdf';
            if (blob) {
                useUIStateStore().showPopup('Saving annotations...', 'info');
                try {
                    const file = new File([blob], filename, { type: 'application/pdf' });
                    await props.datapoint.uploadDocument(file, true);
                    useUIStateStore().showPopup('Annotations saved successfully!', 'success');
                } catch (e) {
                    console.error(e);
                    useUIStateStore().showPopup('Failed to save annotations.', 'error');
                }
            }
        }
    }

    // auto set layout when mounted
    onMounted(() => {
        setLayout(props.layoutType);
        window.addEventListener('message', handleMessage);
    })

    onUnmounted(() => {
        window.removeEventListener('message', handleMessage);
    })

</script>

<template>
    <div id="body">
        <!-- <div class="pane" id="left-pane" ref="leftPane" v-show="showLeftPane"> -->
        <Splitter direction="vertical" 
        v-model:split-ratio="useUIStateStore().preferredReaderLeftPanelWidthPerc"
        splitter-width="4px"
        :mode="({
            0: 'a',
            1: 'b',
            2: 'ab',
        }[layoutType] as 'a'|'b'|'ab')"
        @move-start="()=>isMovingSplitter=true" 
        @move-stop="()=>isMovingSplitter=false"
        overflow="unset"
        >
            <template v-slot:a>
                <!-- pointer event should be none when moving splitter, otherwise the iframe will capture the mouse event -->
                <iframe :src="openDocURL" title="doc" frameborder="0" v-if="datapoint.summary.has_file"
                    :style="{'pointer-events': isMovingSplitter ? 'none' : 'auto'}"
                    :key="iframeKey"
                > </iframe>

                <div style="display: flex; justify-content: center; align-items: center; height: 100%; width: 100%" v-else
                    @dragover="($event)=>$event.preventDefault()"
                    @drop="($ev: DragEvent)=>{
                        $ev.preventDefault();
                        const files = $ev.dataTransfer?.files;
                        useUIStateStore().showPopup('Upload file', 'info');
                        if (files && files.length == 1){
                            datapoint.uploadDocument(files[0]).then(()=>{
                                useUIStateStore().showPopup(
                                    'File uploaded', 'success'
                                )
                            })
                        }
                    }"
                >
                    <div style="color: var(--color-text-soft); font-weight: bold; font-size: large;">No file, 
                        drag and drop to&nbsp;
                    </div>
                    <FileSelectButton :action="(f: File)=>datapoint.uploadDocument(f)" text="upload" :as-link="true" 
                    style="font-weight: bold; font-size: large; cursor: pointer;">
                    </FileSelectButton>
                </div>
            </template>
            <template v-slot:b>
                <div class="tab-container">
                    <div class="tab-header">
                        <div class="tab-title" :class="{active: currentTab==='note'}" @click="currentTab='note'">Note</div>
                        <div class="tab-title" :class="{active: currentTab==='chat'}" @click="currentTab='chat'">Chat</div>
                    </div>
                    <div class="tab-body">
                        <NoteEditor v-show="currentTab === 'note'" :datapoint="datapoint" :auto-enable-edit="true" ref="noteEditor"> </NoteEditor>
                        <ReaderChat v-show="currentTab === 'chat'" :datapoint="datapoint"> </ReaderChat>
                    </div>
                </div>
            </template>
        </Splitter>
    </div>
</template>

<style scoped>
div#body{
    width: 100%;
    height: 100%;
}

iframe{
    width: 100%;
    height: 100%;
    padding: 0px;
    margin: 0px;
}
@media only screen and (max-width: 767px) {
    iframe{
        border-radius: 0px;
    }
}

.tab-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 100%;
    background-color: var(--color-background);
    min-height: 0;
}
.tab-header {
    display: flex;
    flex-direction: row;
    border-bottom: 1px solid var(--color-border);
    background-color: var(--color-background-soft);
    height: 36px;
    flex-shrink: 0;
}
.tab-title {
    padding: 0 20px;
    line-height: 36px;
    cursor: pointer;
    font-size: 0.9em;
    font-weight: 600;
    color: var(--color-text-soft);
    transition: all 0.2s;
    user-select: none;
}
.tab-title:hover {
    color: var(--color-text);
    background-color: var(--color-background-mute);
}
.tab-title.active {
    background-color: var(--color-background);
    color: var(--color-text);
    border-top: 2px solid var(--color-text);
    border-bottom: 1px solid transparent;
    margin-bottom: -1px;
}
.tab-body {
    flex: 1;
    overflow: hidden;
    position: relative;
    min-height: 0;
}
.tab-body > :deep(*) {
    height: 100%;
    width: 100%;
    min-height: 0;
}
</style>